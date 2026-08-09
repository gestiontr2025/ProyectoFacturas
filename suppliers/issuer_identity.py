"""Detección genérica y explicable de emisores desconocidos.

El catálogo JSON continúa siendo la fuente de verdad para proveedores
recurrentes. Este módulo se utiliza únicamente cuando el catálogo no reconoce
al emisor y el comprobante aporta evidencia fiscal suficiente para construir
una identidad ocasional.

La detección no presupone que el emisor esté al principio del PDF. Recorre todo
el texto, reúne candidatos de razón social y los asocia con CUIT argentinos
válidos mediante un sistema de puntajes. Además del puntaje se conservan las
razones que justifican la decisión para facilitar auditorías y depuración.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
import unicodedata

import business_config
from suppliers.cuit import extraer_cuits, normalizar_cuit

_COPY_MARKERS = {"ORIGINAL", "DUPLICADO", "TRIPLICADO", "CUADRUPLICADO"}
_REJECT_EXACT = {
    "FACTURA",
    "FACTURA A",
    "FACTURA B",
    "FACTURA C",
    "NOTA DE CREDITO",
    "NOTA DE CREDITO A",
    "NOTA DE CREDITO B",
    "NOTA DE CREDITO C",
    "NOTA DE DEBITO",
    "NOTA DE DEBITO A",
    "NOTA DE DEBITO B",
    "NOTA DE DEBITO C",
    "RECIBO",
    "CLIENTE",
    "PROVEEDOR",
    "CONTADO",
    "CUIT",
    "CUIT EMISOR",
    "CUIT RECEPTOR",
    "INGRESOS BRUTOS",
    "DOMICILIO",
    "DOMICILIO COMERCIAL",
    "RAZON SOCIAL",
    "NOMBRE DE FANTASIA",
    "CONDICION FRENTE AL IVA",
    "FECHA DE EMISION",
    "FECHA DE INICIO DE ACTIVIDADES",
    "INICIO DE ACTIVIDADES",
    "APELLIDO Y NOMBRE RAZON SOCIAL",
    "PUNTO DE VENTA",
    "COMP NRO",
    "IVA RESPONSABLE INSCRIPTO",
    "NO RESPONSABLE",
    "RESP INSCRIPTO",
    "ING BRUTOS",
    "SENOR CONSORCISTA",
    "ACLARACION Y SELLO",
    "FIRMA AUTORIZADA",
    "DESCRIPCION",
    "CANTIDAD",
    "PRECIO UNIT",
    "SUBTOTAL",
}
_REJECT_CONTAINS = (
    "MADERO ROOF",
    "DOCUMENTO DE PRUEBA",
    "SIN VALIDEZ FISCAL",
    "NO UTILIZAR",
    "RESPONSABLE INSCRIPTO",
    "CONDICION DE VENTA",
    "FECHA DE VTO",
    "PUNTO DE VENTA",
    "COMP NRO",
    "COD ",
    "CAE",
    "COMPROBANTE AUTORIZADO",
    "AGENCIA NO SE RESPONSABILIZA",
    "IMPORTE ",
    "NETO GRAVADO",
    "SUBTOTAL",
    "TOTAL",
    "ALICUOTA",
    "PAG ",
    "PRECIO UNIT",
    "LIQUIDACION DE GASTOS COMUNES",
    "DETALLES DE GASTOS",
    "EMITIR CHEQUES",
    "CHEQUES A LA ORDEN",
    "COMPROBANTE ASOCIADO",
    "FACTURA ASOCIADA",
    "NOTA DE CREDITO ASOCIADA",
    "NOTA DE DEBITO ASOCIADA",
    "DOCUMENTO ASOCIADO",
    "DOCUMENTO RELACIONADO",
    "COMPROBANTE RELACIONADO",
    "COMPROBANTE ORIGINAL",
    "REFERENCIA",
)
_ADDRESS_WORDS = {
    "CALLE", "AV", "AVENIDA", "PISO", "DPTO", "BUENOS", "AIRES", "CABA",
    "CAPITAL", "FEDERAL", "LOCALIDAD", "PROVINCIA", "RUTA", "KM", "DOMICILIO",
}
_LEGAL_SUFFIXES = {
    "SA", "SRL", "SAS", "SE", "SCA", "SH", "SACIF", "SAU", "SOCIEDAD",
    "COOPERATIVA", "CONSORCIO", "COPROPIETARIOS",
}
_EXPLICIT_NAME_LABEL = re.compile(
    r"^(?:APELLIDO\s+Y\s+NOMBRE\s*/?\s*)?RAZON\s+SOCIAL\s*:\s*(.+)$"
)
_TRADE_NAME_LABEL = re.compile(r"^NOMBRE\s+DE\s+FANTASIA\s*:\s*(.+)$")
_CUIT_TEXT_PATTERN = re.compile(
    r"(?<!\d)(\d{2})\s*[-.]?\s*(\d{8})\s*[-.]?\s*(\d)(?!\d)"
)

_DYNAMIC_REJECT_PREFIXES = (
    "CUIT ", "CUIT:", "CUIT EMISOR", "CUIT RECEPTOR",
    "RAZON SOCIAL", "NOMBRE DE FANTASIA",
    "FECHA ", "FECHA:", "FECHA DE EMISION", "VENC",
    "INGRESOS BRUTOS", "INICIO DE ACTIVIDADES", "FECHA DE INICIO",
    "NUMERO ", "NRO ", "NRO.", "NO ", "NO.",
    "PUNTO DE VENTA", "COMP ", "COMPROBANTE ",
    "CLIENTE ", "RECEPTOR ", "DESTINATARIO ",
    "TOTAL ", "NETO ", "IVA ", "CAE ", "MOTIVO ",
)

_DOCUMENT_PREFIX_PATTERN = re.compile(
    r"^(?:(?:FACTURA|NOTA\s+(?:DE\s+)?CREDITO|NOTA\s+(?:DE\s+)?DEBITO|REMITO|RECIBO)"
    r"(?:\s+[ABC]\b)?\s*[-:–—]*\s*)+"
)


@dataclass(frozen=True)
class IssuerIdentity:
    cuit: str
    legal_name: str
    score: int
    evidence: tuple[str, ...]


@dataclass(frozen=True)
class _NameCandidate:
    name: str
    line_index: int
    base_score: int
    evidence: tuple[str, ...]


def _ascii_upper(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    without_marks = "".join(c for c in normalized if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", without_marks.upper()).strip()


def _clean_line(value: str) -> str:
    line = _ascii_upper(value)
    line = re.sub(r"^[\s:;,.-]+|[\s:;,.-]+$", "", line)
    return re.sub(r"\s+", " ", line)


def _lines(text: str) -> list[str]:
    return [_clean_line(line) for line in (text or "").splitlines() if _clean_line(line)]


def _normalized_words(value: str) -> list[str]:
    normalized = _ascii_upper(value)
    # Unificar formas jurídicas puntuadas antes de separar palabras.
    normalized = re.sub(r"\bS\s*\.\s*R\s*\.\s*L\s*\.?", " SRL ", normalized)
    normalized = re.sub(r"\bS\s*\.\s*A\s*\.\s*S\s*\.?", " SAS ", normalized)
    normalized = re.sub(r"\bS\s*\.\s*A\s*\.?", " SA ", normalized)
    return re.findall(r"[A-Z]{2,}", re.sub(r"[^A-Z0-9]+", " ", normalized))


def _is_name_candidate(line: str) -> bool:
    normalized = re.sub(r"[^A-Z0-9]+", " ", line).strip()
    if not normalized or normalized in _COPY_MARKERS or normalized in _REJECT_EXACT:
        return False
    if any(fragment in normalized for fragment in _REJECT_CONTAINS):
        return False
    if any(normalized.startswith(prefix) for prefix in _DYNAMIC_REJECT_PREFIXES):
        return False
    if re.search(r"\b\d{2}[/-]\d{2}[/-]\d{2,4}\b", normalized):
        return False
    if re.fullmatch(r"[\d .,/$%\-]+", line):
        return False
    if "@" in line or "WWW" in normalized or "HTTP" in normalized:
        return False
    if len(normalized) > 110:
        return False

    words = _normalized_words(normalized)
    if len(words) < 2:
        return False
    if sum(word in _ADDRESS_WORDS for word in words) >= 2:
        return False
    return True


def _candidate_key(name: str) -> str:
    return re.sub(r"[^A-Z0-9]+", " ", _ascii_upper(name)).strip()


def _add_candidate(
    target: dict[str, _NameCandidate],
    *,
    name: str,
    index: int,
    score: int,
    evidence: list[str],
) -> None:
    cleaned = _clean_line(name)
    # El OCR puede pegar el tipo documental al nombre del emisor, p. ej.
    # ``NOTA DE CREDITO CONSTRUCCIONES KAISA S.A.``. El tipo no forma parte
    # de la razón social y se elimina antes del scoring/naming.
    cleaned = _DOCUMENT_PREFIX_PATTERN.sub("", cleaned).strip()
    if cleaned.startswith("CONSORCIO DE "):
        # El OCR suele pegar la numeración del inmueble al beneficiario:
        # ``CONSORCIO DE COP COSSETTINI 703/787``. Esa fracción identifica la
        # dirección, no forma parte estable de la razón social y produciría
        # carpetas duplicadas para el mismo CUIT.
        cleaned = re.sub(r"\s+\d{2,4}\s*/\s*\d{2,4}$", "", cleaned).strip()
    if not _is_name_candidate(cleaned):
        return
    key = _candidate_key(cleaned)
    previous = target.get(key)
    candidate = _NameCandidate(cleaned, index, score, tuple(evidence))
    if previous is None or candidate.base_score > previous.base_score:
        target[key] = candidate


def _collect_name_candidates(lines: list[str]) -> list[_NameCandidate]:
    """Reunir nombres candidatos en todo el documento, no solo en el encabezado."""
    candidates: dict[str, _NameCandidate] = {}

    # Los consorcios suelen imprimir la denominación legal partida en varias
    # líneas (CONSORCIO / COPROPIETARIOS / dirección o nombre del edificio).
    # Componer ese encabezado es más fiable que tomar una línea OCR aislada.
    for index, line in enumerate(lines):
        if line != "CONSORCIO":
            continue
        window_end = min(len(lines), index + 6)
        copro_index = next(
            (i for i in range(index + 1, window_end) if "COPROPIETARIOS" in lines[i]),
            None,
        )
        if copro_index is None:
            continue
        parts = [line, lines[copro_index]]
        # El nombre o dirección identificatoria puede quedar una o dos líneas
        # después de COPROPIETARIOS por el orden de lectura del OCR.
        for candidate_index in range(copro_index + 1, min(len(lines), copro_index + 4)):
            candidate_line = lines[candidate_index]
            if _is_name_candidate(candidate_line) and not re.search(r"\bN[°O]?\.?\s*\d", candidate_line):
                parts.append(candidate_line)
                break
        _add_candidate(
            candidates,
            name=" ".join(parts),
            index=index,
            score=13,
            evidence=["denominacion_consorcio_compuesta"],
        )

    for index, line in enumerate(lines):
        # En liquidaciones de expensas la denominación del emisor suele
        # repetirse como beneficiario de pago en una sola línea y el OCR la
        # conserva mejor que el membrete superior partido en columnas.
        consorcio_match = re.search(
            r"\b(CONSORCIO\s+DE\s+[A-Z][A-Z0-9 .&-]*?)(?=\s+\d{2,4}\s*/\s*\d{2,4}\b|$)",
            line,
        )
        if consorcio_match:
            _add_candidate(
                candidates,
                name=consorcio_match.group(1),
                index=index,
                score=15,
                evidence=["denominacion_consorcio_explicita"],
            )

        explicit = _EXPLICIT_NAME_LABEL.match(line)
        if explicit:
            _add_candidate(
                candidates,
                name=explicit.group(1),
                index=index,
                score=10,
                evidence=["razon_social_explicita_en_misma_linea"],
            )
            continue

        if line in {"RAZON SOCIAL", "APELLIDO Y NOMBRE RAZON SOCIAL"} and index + 1 < len(lines):
            _add_candidate(
                candidates,
                name=lines[index + 1],
                index=index + 1,
                score=9,
                evidence=["razon_social_explicita_en_linea_siguiente"],
            )

        trade = _TRADE_NAME_LABEL.match(line)
        if trade:
            _add_candidate(
                candidates,
                name=trade.group(1),
                index=index,
                score=4,
                evidence=["nombre_fantasia_explicito"],
            )

        if index > 0 and lines[index - 1] in _COPY_MARKERS:
            # En comprobantes ARCA el emisor suele aparecer inmediatamente
            # después de ORIGINAL/DUPLICADO/TRIPLICADO.
            _add_candidate(
                candidates,
                name=line,
                index=index,
                score=12,
                evidence=["inmediatamente_despues_de_marca_de_copia"],
            )

        # Patrón genérico muy frecuente: razón social en una línea y CUIT en
        # la siguiente. No requiere literalmente la etiqueta ``Razón Social``.
        # Si además el CUIT dice ``emisor``, la señal es todavía más fuerte.
        if index + 1 < len(lines) and _CUIT_TEXT_PATTERN.search(lines[index + 1]):
            cuit_line = lines[index + 1]
            # Para un CUIT genérico exigimos que la línea anterior parezca un
            # nombre puro (sin importes/códigos). ``CUIT EMISOR`` ya aporta una
            # etiqueta semántica fuerte y admite una regla más directa.
            previous_words = _normalized_words(line)
            looks_like_clean_name = (
                not re.search(r"\d", line)
                and 2 <= len(previous_words) <= 8
            )
            if looks_like_clean_name:
                score = 11 if "CUIT EMISOR" in cuit_line else 8
                evidence = [
                    "nombre_inmediatamente_antes_del_cuit",
                    "cuit_emisor_explicito" if "CUIT EMISOR" in cuit_line else "cuit_en_linea_siguiente",
                ]
                _add_candidate(
                    candidates,
                    name=line,
                    index=index,
                    score=score,
                    evidence=evidence,
                )

        if not _is_name_candidate(line):
            continue

        words = _normalized_words(line)
        score = 1
        evidence = ["texto_con_estructura_de_nombre"]
        if any(word in _LEGAL_SUFFIXES for word in words):
            score += 4
            evidence.append("forma_juridica")
            if words and words[0] == "CONSORCIO":
                score += 3
                evidence.append("denominacion_consorcio")
        elif 3 <= len(words) <= 5:
            score += 2
            evidence.append("estructura_nombre_persona")

        if index + 1 < len(lines):
            next_line = lines[index + 1]
            if any(word in next_line for word in ("CALLE", "AVENIDA", "BUENOS AIRES", "CABA", "PISO")):
                score += 2
                evidence.append("seguido_por_domicilio")

        _add_candidate(
            candidates,
            name=line,
            index=index,
            score=score,
            evidence=evidence,
        )

    return list(candidates.values())




def _receiver_cuits_by_name_context(lines: list[str]) -> set[str]:
    """Detectar CUIT ligados visualmente al receptor aunque el dígito difiera.

    El CUIT canónico sigue siendo la fuente de verdad. Esta ayuda existe para
    OCR: si una línea dice explícitamente MADERO ROOF TOP y junto a ella aparece
    otro CUIT válido, ese número pertenece al bloque receptor y no debe competir
    como emisor ocasional. Nunca convierte ese CUIT en dato canónico; solo lo
    excluye del conjunto de candidatos.
    """
    result: set[str] = set()
    for index, line in enumerate(lines):
        if "MADERO ROOF" not in line:
            continue
        for candidate_index in range(index, min(len(lines), index + 2)):
            for cuit in extraer_cuits(lines[candidate_index]):
                result.add(cuit)
    return result


def _find_cuit_line_indices(lines: list[str], cuit: str) -> list[int]:
    """Localizar el CUIT como campo, no como fragmento de un código de barras.

    Un comprobante puede incluir una tira numérica que contiene el CUIT dentro
    de 40 o 50 dígitos. Usar una búsqueda por subcadena hacía que texto OCR
    cercano al código de barras pareciera estar junto al CUIT y recibiera un
    puntaje artificialmente alto.
    """

    target = re.sub(r"\D", "", cuit)
    result: list[int] = []
    for index, line in enumerate(lines):
        for match in _CUIT_TEXT_PATTERN.finditer(line):
            candidate = "".join(match.groups())
            if candidate == target:
                result.append(index)
                break
    return result


def _page_wide_fiscal_evidence(lines: list[str]) -> tuple[int, list[str]]:
    joined = "\n".join(lines)
    score = 0
    evidence: list[str] = []
    checks = (
        (r"\bPUNTO DE VENTA\b", 2, "punto_de_venta"),
        (r"\bCOMP(?:ROBANTE)?\.?\s*NRO\b|\bCOMP NRO\b", 2, "numero_comprobante"),
        (r"\bFECHA DE EMISION\b", 1, "fecha_emision"),
        (r"\bCONDICION FRENTE AL IVA\b|\bIVA RESPONSABLE INSCRIPTO\b", 1, "condicion_iva"),
        (r"\bINICIO DE ACTIVIDADES\b|\bFECHA DE INICIO DE ACTIVIDADES\b", 1, "inicio_actividades"),
        (r"\bINGRESOS BRUTOS\b", 1, "ingresos_brutos"),
    )
    for pattern, points, reason in checks:
        if re.search(pattern, joined):
            score += points
            evidence.append(reason)
    return score, evidence


def _score_name_for_cuit(
    candidate: _NameCandidate,
    cuit_indices: list[int],
    lines: list[str],
) -> tuple[int, tuple[str, ...]]:
    score = candidate.base_score
    evidence = list(candidate.evidence)

    if cuit_indices:
        distance = min(abs(candidate.line_index - index) for index in cuit_indices)
        if distance <= 1:
            score += 7
            evidence.append("nombre_junto_al_cuit")
        elif distance <= 4:
            score += 5
            evidence.append("nombre_muy_cercano_al_cuit")
        elif distance <= 10:
            score += 3
            evidence.append("nombre_cercano_al_cuit")
        elif distance <= 20:
            score += 1
            evidence.append("nombre_en_misma_seccion_del_cuit")

    # Etiquetas explícitas del CUIT aportan evidencia adicional.
    for index in cuit_indices:
        line = lines[index]
        previous = lines[index - 1] if index > 0 else ""
        if "CUIT EMISOR" in line or "CUIT EMISOR" in previous:
            score += 5
            evidence.append("cuit_etiquetado_como_emisor")
            break
        if line.startswith("CUIT") or previous == "CUIT":
            score += 2
            evidence.append("cuit_con_etiqueta")
            break

    return score, tuple(dict.fromkeys(evidence))


def _best_name_for_cuit(
    cuit: str,
    lines: list[str],
    candidates: list[_NameCandidate],
) -> tuple[str | None, int, tuple[str, ...]]:
    indices = _find_cuit_line_indices(lines, cuit)
    scored: list[tuple[int, int, str, tuple[str, ...]]] = []
    for candidate in candidates:
        score, evidence = _score_name_for_cuit(candidate, indices, lines)
        scored.append((score, -candidate.line_index, candidate.name, evidence))

    if not scored:
        return None, 0, ()
    scored.sort(reverse=True)
    best_score, _neg_index, best_name, best_evidence = scored[0]

    # Si dos nombres diferentes quedan prácticamente empatados, no elegimos de
    # forma arbitraria. Una razón social explícita puede desempatar a un nombre
    # de fantasía, pero una diferencia mínima entre candidatos similares se
    # considera ambigua.
    if len(scored) > 1:
        second_score, _second_index, second_name, second_evidence = scored[1]
        if second_name != best_name and second_score >= best_score - 1:
            # Una denominación explícita puede convivir con el mismo nombre
            # fragmentado por OCR. No es una ambigüedad real: es la misma
            # entidad expresada con distinta calidad de lectura.
            explicit_best = any(
                reason in best_evidence
                for reason in (
                    "razon_social_explicita_en_misma_linea",
                    "razon_social_explicita_en_linea_siguiente",
                    "denominacion_consorcio_explicita",
                )
            )
            second_is_fragment = "denominacion_consorcio_compuesta" in second_evidence
            if not (explicit_best and second_is_fragment):
                return None, best_score, best_evidence + ("nombres_candidatos_ambiguos",)

    return best_name, best_score, best_evidence


def extraer_identidad_emisor(text: str, cuit_hint: str | None = None) -> IssuerIdentity | None:
    """Detectar un emisor nuevo mediante CUIT válido y evidencia ponderada.

    La decisión automática requiere:

    * exactamente un CUIT tercero válido después de excluir al receptor;
    * un nombre candidato con puntaje suficiente;
    * evidencia fiscal global en el documento;
    * ausencia de empate entre nombres candidatos.
    """
    third_party_cuits: list[str] = []
    lines = _lines(text)
    receiver_context_cuits = _receiver_cuits_by_name_context(lines)

    normalized_hint = normalizar_cuit(cuit_hint)
    if (
        normalized_hint
        and not business_config.es_cuit_receptor(normalized_hint)
        and normalized_hint not in receiver_context_cuits
    ):
        third_party_cuits.append(normalized_hint)

    for cuit in extraer_cuits(text):
        if (
            business_config.es_cuit_receptor(cuit)
            or cuit in receiver_context_cuits
            or cuit in third_party_cuits
        ):
            continue
        third_party_cuits.append(cuit)

    # Con varios CUIT de terceros no hay forma segura de saber cuál es el
    # emisor sin información adicional (intermediarios, transportistas, etc.).
    if len(third_party_cuits) != 1:
        return None

    name_candidates = _collect_name_candidates(lines)
    legal_name, name_score, name_evidence = _best_name_for_cuit(
        third_party_cuits[0], lines, name_candidates
    )
    if not legal_name:
        return None

    fiscal_score, fiscal_evidence = _page_wide_fiscal_evidence(lines)
    total_score = 8 + name_score + fiscal_score
    evidence = tuple(dict.fromkeys(
        ("cuit_valido_distinto_del_receptor",) + name_evidence + tuple(fiscal_evidence)
    ))

    # Umbral conservador: exige más que un CUIT y un texto con aspecto de
    # nombre. Los tres diseños de prueba superan holgadamente este valor.
    if total_score < 18:
        return None

    return IssuerIdentity(
        cuit=third_party_cuits[0],
        legal_name=legal_name,
        score=total_score,
        evidence=evidence,
    )
