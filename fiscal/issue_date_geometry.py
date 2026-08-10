"""Detección geométrica de fecha de emisión en PDF digitales.

Este módulo NO hace OCR. Usa las coordenadas de palabras que PyMuPDF obtiene
cuando el PDF ya contiene una capa de texto. Su objetivo es recuperar la
relación visual entre una etiqueta (por ejemplo ``FECHA DE EMISION``) y su
valor cuando la extracción lineal de pypdf aplana columnas o altera su orden.

La geometría se usa como evidencia adicional de auditoría. Nunca convierte una
fecha de vencimiento, CAE, período facturado o inicio de actividad en fecha de
emisión.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re
import unicodedata

try:
    import pymupdf
except ImportError:  # pragma: no cover - dependencia opcional en ejecución
    pymupdf = None


_DATE_RE = re.compile(r"\b(\d{1,2}[./-]\d{1,2}[./-](?:\d{4}|\d{2}))\b")


@dataclass(frozen=True)
class GeometryDateCandidate:
    issue_date: str
    score: int
    reason: str
    page: int
    x: float
    y: float


def _norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.upper()
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def _parse_date(value: str) -> str | None:
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%d/%m/%y", "%d-%m-%y"):
        try:
            return datetime.strptime(value, fmt).strftime("%d/%m/%Y")
        except ValueError:
            pass
    return None


def _contains_secondary_label(text: str) -> bool:
    text = _norm(text)
    patterns = (
        r"\bVTO\b",
        r"\bVENC(?:IMIENTO)?\b",
        r"FECHA\s+DE\s+VTO",
        r"VTO\.?\s+PARA\s+EL\s+PAGO",
        r"\bCAE\b",
        r"PERIODO\s+FACTURADO",
        r"PERIODO\s+DESDE",
        r"PERIODO\s+HASTA",
        r"INICIO\s+(?:DE\s+)?ACTIV",
        r"FECHA\s+DE\s+INICIO",
        r"\bENTREGA\b",
    )
    return any(re.search(pattern, text) for pattern in patterns)


def _is_issue_label(text: str) -> bool:
    text = _norm(text)
    return bool(
        re.search(
            r"FECHA\s+(?:DE\s+)?(?:EMISION|DEL\s+COMPROBANTE|DEL\s+DOCUMENTO)",
            text,
        )
    )


def _is_generic_date_label(text: str) -> bool:
    text = _norm(text)
    return bool(re.search(r"\bFECHA\b", text)) and not _contains_secondary_label(text)


def _is_fiscal_header(text: str) -> bool:
    text = _norm(text)
    return bool(
        re.search(r"\b(?:FACTURA|NOTA\s+DE\s+(?:CREDITO|DEBITO))\b", text)
        or re.search(r"\b(?:NRO|NUMERO|COMP\.?\s*NRO)\b", text)
        or re.search(r"\b[ABC]\s*\d{1,5}\s*[-/]\s*\d{1,8}\b", text)
    )


def _horizontal_overlap(a0: float, a1: float, b0: float, b1: float, padding: float = 28.0) -> bool:
    return not (a1 + padding < b0 or b1 + padding < a0)


def _center_distance(a0: float, a1: float, b0: float, b1: float) -> float:
    return abs(((a0 + a1) / 2.0) - ((b0 + b1) / 2.0))


def _build_lines(words):
    grouped: dict[tuple[int, int], list[tuple]] = {}
    for word in words:
        if len(word) < 8:
            continue
        grouped.setdefault((int(word[5]), int(word[6])), []).append(word)

    lines = []
    for key, items in grouped.items():
        items.sort(key=lambda w: w[0])
        text = " ".join(str(w[4]) for w in items)
        lines.append(
            {
                "key": key,
                "words": items,
                "text": text,
                "norm": _norm(text),
                "x0": min(float(w[0]) for w in items),
                "y0": min(float(w[1]) for w in items),
                "x1": max(float(w[2]) for w in items),
                "y1": max(float(w[3]) for w in items),
            }
        )
    lines.sort(key=lambda line: (line["y0"], line["x0"]))
    return lines


def _candidate_from_word(line, word, date_text: str, all_lines, page_number: int):
    parsed = _parse_date(date_text)
    if not parsed:
        return None

    x0, y0, x1, y1 = map(float, word[:4])
    same = line["norm"]

    # Una etiqueta secundaria en la misma línea es veto fuerte.
    if _contains_secondary_label(same):
        return None

    # Etiqueta inequívoca en la misma línea.
    if _is_issue_label(same):
        return GeometryDateCandidate(
            parsed, 100, "geometría: fecha en la misma línea que etiqueta explícita de emisión",
            page_number, x0, y0,
        )

    nearby_above = []
    nearby_same = []
    nearby_context = []
    for other in all_lines:
        if other is line:
            continue
        vertical = y0 - other["y1"]
        if -10 <= vertical <= 55:
            if _horizontal_overlap(x0, x1, other["x0"], other["x1"], padding=42):
                nearby_above.append(other)
            if _center_distance(x0, x1, other["x0"], other["x1"]) <= 150:
                nearby_context.append(other)
        if abs(((line["y0"] + line["y1"]) / 2) - ((other["y0"] + other["y1"]) / 2)) <= 7:
            nearby_same.append(other)

    # PyMuPDF puede separar etiqueta y valor en bloques distintos aunque estén
    # visualmente en la misma fila. Una etiqueta explícita de emisión en esa
    # misma fila es la relación campo-valor más fuerte disponible.
    issue_same = [
        other for other in nearby_same
        if _is_issue_label(other["norm"]) and not _contains_secondary_label(other["norm"])
    ]
    if issue_same:
        closest_same = min(
            issue_same,
            key=lambda other: _center_distance(x0, x1, other["x0"], other["x1"]),
        )
        if _center_distance(x0, x1, closest_same["x0"], closest_same["x1"]) <= 150:
            return GeometryDateCandidate(
                parsed, 100,
                "geometría: fecha en la misma fila que etiqueta explícita de emisión",
                page_number, x0, y0,
            )

    # Si la columna que contiene la fecha está debajo de una etiqueta
    # secundaria, se descarta aunque cerca exista otra etiqueta de emisión.
    secondary_above = [
        other for other in nearby_above
        if _contains_secondary_label(other["norm"])
        and _center_distance(x0, x1, other["x0"], other["x1"]) <= 110
    ]
    if secondary_above:
        return None

    issue_above = [
        other for other in nearby_above
        if _is_issue_label(other["norm"])
    ]
    if issue_above:
        closest = min(
            issue_above,
            key=lambda other: (
                max(0.0, y0 - other["y1"]),
                _center_distance(x0, x1, other["x0"], other["x1"]),
            ),
        )
        if max(0.0, y0 - closest["y1"]) <= 45 and _center_distance(x0, x1, closest["x0"], closest["x1"]) <= 120:
            return GeometryDateCandidate(
                parsed, 99,
                "geometría: fecha ubicada debajo de etiqueta explícita de emisión",
                page_number, x0, y0,
            )

    # Etiqueta genérica Fecha es solo evidencia media/alta si está dentro de
    # una cabecera fiscal. Nunca alcanza 96 por sí sola.
    generic_near = _is_generic_date_label(same) or any(
        _is_generic_date_label(other["norm"]) for other in nearby_above + nearby_same
    )
    fiscal_near = _is_fiscal_header(same) or any(
        _is_fiscal_header(other["norm"]) for other in nearby_context + nearby_same
    )
    if generic_near and fiscal_near:
        return GeometryDateCandidate(
            parsed, 91, "geometría: etiqueta Fecha dentro de cabecera fiscal",
            page_number, x0, y0,
        )
    if generic_near:
        return GeometryDateCandidate(
            parsed, 76, "geometría: etiqueta Fecha genérica",
            page_number, x0, y0,
        )

    return None


def extract_geometry_date_candidates(path: str | Path, *, max_pages: int = 2) -> tuple[GeometryDateCandidate, ...]:
    """Extraer candidatos visuales de fecha sin OCR.

    Devuelve solo candidatos con alguna relación geométrica significativa con
    etiquetas de fecha. Los PDF sin texto digital o sin PyMuPDF devuelven una
    tupla vacía.
    """

    if pymupdf is None:
        return ()

    path = Path(path)
    candidates: list[GeometryDateCandidate] = []
    try:
        document = pymupdf.open(path)
    except Exception:
        return ()

    try:
        for page_index in range(min(len(document), max_pages)):
            page = document[page_index]
            words = page.get_text("words") or []
            if not words:
                continue
            lines = _build_lines(words)
            for line in lines:
                for word in line["words"]:
                    raw = str(word[4])
                    matches = list(_DATE_RE.finditer(raw))
                    if not matches:
                        continue
                    for match in matches:
                        candidate = _candidate_from_word(
                            line, word, match.group(1), lines, page_index + 1
                        )
                        if candidate is not None:
                            candidates.append(candidate)
    finally:
        document.close()

    # Consolidar por fecha: conservar la evidencia geométrica más fuerte.
    best: dict[str, GeometryDateCandidate] = {}
    for candidate in candidates:
        existing = best.get(candidate.issue_date)
        if existing is None or candidate.score > existing.score:
            best[candidate.issue_date] = candidate

    return tuple(sorted(best.values(), key=lambda c: (-c.score, c.page, c.y, c.x)))
