"""Extracción genérica de la identidad fiscal de un emisor desconocido.

El catálogo sigue siendo la fuente de verdad para proveedores recurrentes. Si
una factura válida pertenece a un CUIT todavía ausente del catálogo, este
módulo intenta obtener una razón social del encabezado fiscal sin persistirla
ni inventarla a partir del nombre del archivo.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata

import business_config
from suppliers.cuit import extraer_cuits, normalizar_cuit

_HEADER_END_MARKERS = (
    "CODIGO PRODUCTO",
    "CODIGO PRODUCTO / SERVICIO",
    "DETALLE DE PRODUCTOS",
    "DESCRIPCION CANTIDAD",
    "CANT. DESCRIPCION",
)
_COPY_MARKERS = {"ORIGINAL", "DUPLICADO", "TRIPLICADO", "CUADRUPLICADO"}
_REJECT_EXACT = {
    "FACTURA",
    "NOTA DE CREDITO",
    "NOTA DE DEBITO",
    "RECIBO",
    "CONTADO",
    "CUIT",
    "INGRESOS BRUTOS",
    "DOMICILIO COMERCIAL",
    "RAZON SOCIAL",
    "CONDICION FRENTE AL IVA",
    "FECHA DE EMISION",
    "FECHA DE INICIO DE ACTIVIDADES",
    "APELLIDO Y NOMBRE RAZON SOCIAL",
    "PUNTO DE VENTA COMP NRO",
    "IVA RESPONSABLE INSCRIPTO",
}
_REJECT_CONTAINS = (
    "MADERO ROOF",
    "RESPONSABLE INSCRIPTO",
    "CONDICION DE VENTA",
    "DOMICILIO",
    "FECHA DE",
    "PUNTO DE VENTA",
    "COMP NRO",
    "COD ",
    "CAE",
    "COMPROBANTE AUTORIZADO",
    "AGENCIA NO SE RESPONSABILIZA",
    "IMPORTE ",
    "SUBTOTAL",
    "TOTAL",
    "ALICUOTA",
    "PAG ",
)
_ADDRESS_WORDS = {
    "CALLE", "AV", "AVENIDA", "PISO", "DPTO", "BUENOS", "AIRES", "CABA",
    "CAPITAL", "FEDERAL", "LOCALIDAD", "PROVINCIA", "RUTA", "KM",
}
_LEGAL_SUFFIXES = {
    "SA", "SRL", "SAS", "SE", "SCA", "SH", "SOCIEDAD", "COOPERATIVA",
}


@dataclass(frozen=True)
class IssuerIdentity:
    cuit: str
    legal_name: str
    score: int
    evidence: tuple[str, ...]


def _ascii_upper(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    without_marks = "".join(c for c in normalized if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", without_marks.upper()).strip()


def _clean_line(value: str) -> str:
    line = _ascii_upper(value)
    line = re.sub(r"^[\s:;,.\-]+|[\s:;,.\-]+$", "", line)
    return re.sub(r"\s+", " ", line)


def _header_lines(text: str) -> list[str]:
    lines = [_clean_line(line) for line in (text or "").splitlines()]
    lines = [line for line in lines if line]
    result: list[str] = []
    for line in lines[:80]:
        normalized = re.sub(r"[^A-Z0-9]+", " ", line).strip()
        if any(marker in normalized for marker in _HEADER_END_MARKERS):
            break
        result.append(line)
    return result


def _is_name_candidate(line: str) -> bool:
    normalized = re.sub(r"[^A-Z0-9]+", " ", line).strip()
    if not normalized or normalized in _COPY_MARKERS or normalized in _REJECT_EXACT:
        return False
    if any(fragment in normalized for fragment in _REJECT_CONTAINS):
        return False
    if re.search(r"\b\d{2}[/-]\d{2}[/-]\d{2,4}\b", normalized):
        return False
    if re.fullmatch(r"[\d .,/\-]+", line):
        return False
    if "@" in line or "WWW" in normalized or "HTTP" in normalized:
        return False

    words = re.findall(r"[A-Z]{2,}", normalized)
    if len(words) < 2:
        return False
    if len(normalized) > 100:
        return False

    address_hits = sum(word in _ADDRESS_WORDS for word in words)
    if address_hits >= 2:
        return False
    return True


def _candidate_score(line: str, index: int, lines: list[str]) -> tuple[int, list[str]]:
    score = 0
    evidence: list[str] = []
    normalized = re.sub(r"[^A-Z0-9]+", " ", line).strip()
    words = normalized.split()

    if index <= 6:
        score += 5
        evidence.append("nombre_en_primeras_lineas")
    elif index <= 14:
        score += 3
        evidence.append("nombre_en_encabezado")

    if index > 0 and lines[index - 1] in _COPY_MARKERS:
        score += 5
        evidence.append("inmediatamente_despues_de_original")

    if any(word in _LEGAL_SUFFIXES for word in words):
        score += 3
        evidence.append("forma_juridica")
    elif 3 <= len(words) <= 5:
        # Nombres de personas físicas suelen tener apellido y dos nombres.
        score += 2
        evidence.append("estructura_nombre_persona")

    if index + 1 < len(lines):
        next_line = lines[index + 1]
        if any(word in next_line for word in ("CALLE", "AVENIDA", "BUENOS AIRES", "CABA")):
            score += 2
            evidence.append("seguido_por_domicilio")

    return score, evidence


def _find_legal_name(text: str) -> tuple[str | None, int, tuple[str, ...]]:
    lines = _header_lines(text)
    candidates: list[tuple[int, int, str, tuple[str, ...]]] = []
    for index, line in enumerate(lines):
        if not _is_name_candidate(line):
            continue
        score, evidence = _candidate_score(line, index, lines)
        candidates.append((score, -index, line, tuple(evidence)))

    if not candidates:
        return None, 0, ()
    candidates.sort(reverse=True)
    score, _negative_index, name, evidence = candidates[0]
    if score < 7:
        return None, score, evidence
    return name, score, evidence


def extraer_identidad_emisor(text: str, cuit_hint: str | None = None) -> IssuerIdentity | None:
    """Detectar un emisor nuevo solo cuando CUIT y razón social son sólidos."""
    candidates: list[str] = []
    normalized_hint = normalizar_cuit(cuit_hint)
    if normalized_hint and not business_config.es_cuit_receptor(normalized_hint):
        candidates.append(normalized_hint)

    for cuit in extraer_cuits(text):
        if business_config.es_cuit_receptor(cuit) or cuit in candidates:
            continue
        candidates.append(cuit)

    # Un único CUIT emisor válido es una condición defensiva importante. Si el
    # documento menciona varios terceros no elegimos uno arbitrariamente.
    if len(candidates) != 1:
        return None

    legal_name, name_score, name_evidence = _find_legal_name(text)
    if not legal_name:
        return None

    score = 6 + name_score
    evidence = ("cuit_valido_distinto_del_receptor",) + name_evidence
    return IssuerIdentity(
        cuit=candidates[0],
        legal_name=legal_name,
        score=score,
        evidence=evidence,
    )
