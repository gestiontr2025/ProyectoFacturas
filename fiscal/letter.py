"""Detección defensiva de la letra fiscal A, B o C."""

import re
from typing import Optional

from fiscal.definitions import AFIP_CODE_TO_TYPE_AND_LETTER, SUPPORTED_LETTERS
from fiscal.normalization import normalizar_para_busqueda
from fiscal.type_detector import detectar_tipo_comprobante

_LETTER_CLASS = "".join(SUPPORTED_LETTERS)


def _detectar_por_codigo_arca(texto: str, tipo: str) -> Optional[str]:
    for match in re.finditer(
        r"(?:COD(?:IGO)?|TIPO)\.?\s*(?:N(?:RO)?\.?\s*)?[:\-]?\s*0*(\d{1,3})\b",
        texto,
    ):
        mapping = AFIP_CODE_TO_TYPE_AND_LETTER.get(int(match.group(1)))
        if mapping and mapping[0] == tipo:
            return mapping[1]
    return None


def _detectar_letra_aislada_ocr(texto_original: str, tipo: str | None) -> Optional[str]:
    """Recuperar una letra grande que OCR dejó separada del título.

    En diseños gráficos la A/B/C vive en un recuadro y Tesseract puede devolver
    una línea aislada ``A`` mientras ``FACTURA`` queda varias líneas después.
    También puede pegarla al nombre del emisor (``EVENTOS MANON A``). Solo se
    acepta dentro del encabezado, antes del bloque receptor, con evidencia
    fiscal ya confirmada y sin ambigüedad entre letras.
    """
    if not tipo:
        return None

    raw_lines = [line.strip() for line in (texto_original or "").splitlines() if line.strip()]
    if not raw_lines:
        return None

    # El encabezado termina cuando comienza el receptor/cliente.
    header: list[str] = []
    for line in raw_lines[:20]:
        upper = normalizar_para_busqueda(line)
        if re.search(r"\b(?:RECEPTOR|CLIENTE|DESTINATARIO|SENOR CONSORCISTA)\b", upper):
            break
        header.append(line)

    if not header:
        return None

    joined = normalizar_para_busqueda("\n".join(header))
    if not re.search(r"\b(?:FACTURA|NOTA|NUMERO|NRO|CAE|CUIT|IVA|TOTAL\s+(?:CREDITO|DEBITO))\b", joined):
        return None
    # Una letra aislada solo se vuelve fiscal cuando el documento también
    # expone una numeración completa. Esto evita interpretar una A de dirección
    # o piso como letra de comprobante.
    if not re.search(r"\b\d{4,5}\s*[-/]\s*\d{6,8}\b", normalizar_para_busqueda(texto_original)):
        return None

    found: list[str] = []
    for line in header:
        normalized = normalizar_para_busqueda(line)
        if normalized in SUPPORTED_LETTERS:
            found.append(normalized)
            continue

        # OCR puede devolver ``EVENTOS MANON A``. Evitamos sociedades del tipo
        # ``S.A.`` comprobando el texto original antes de aceptar la letra final.
        if re.search(r"S\s*\.\s*A\s*\.?\s*$", line.upper()):
            continue
        match = re.search(rf"\b([{_LETTER_CLASS}])\s*$", normalized)
        if match and len(normalized.split()) >= 2:
            found.append(match.group(1))

    unique = list(dict.fromkeys(found))
    return unique[0] if len(unique) == 1 else None


def detectar_letra_comprobante(texto: str) -> Optional[str]:
    """Detectar A, B o C únicamente con contexto fiscal suficiente."""
    texto_original = texto if isinstance(texto, str) else ""
    texto = normalizar_para_busqueda(texto_original)
    if not texto:
        return None

    tipo = detectar_tipo_comprobante(texto)
    letter = rf"([{_LETTER_CLASS}])"

    patterns = (
        rf"\b(?:FACTURA|NOTA\s+(?:DE\s+)?CREDITO|NOTA\s+(?:DE\s+)?DEBITO)\s*[-:]?\s*{letter}\b",
        rf"\b{letter}\s+(?:COD(?:IGO)?\.?\s*0*\d{{1,3}}\s+)?(?:FACTURA|NOTA\s+(?:DE\s+)?CREDITO|NOTA\s+(?:DE\s+)?DEBITO)\b",
        rf"\b(?:FC|FAC|NC|ND)\s*[-_/ ]*{letter}\b",
        rf"\bFA\s*[-_/\"']+{letter}\b",
        rf"\bLETRA\s*[:\-]?\s*{letter}\b",
    )
    for pattern in patterns:
        match = re.search(pattern, texto)
        if match:
            return match.group(1)

    if tipo:
        letter_by_code = _detectar_por_codigo_arca(texto, tipo)
        if letter_by_code:
            return letter_by_code

        isolated = _detectar_letra_aislada_ocr(texto_original, tipo)
        if isolated:
            return isolated

        if "LIQUIDACION DE GASTOS COMUNES" in texto:
            has_number = re.search(
                r"\bN[ROº°]*\.?\s*[:;,.-]?\s*\d{1,5}\s*[-/]\s*\d{1,8}\b",
                texto,
            )
            has_vat = re.search(r"\bIVA\s+(?:21|27)\s*%", texto)
            if has_number and has_vat:
                if re.search(r"(?:^|\s)A(?:\s|$)", texto) or re.search(r'\bA\s*["\']A["\']\b', texto):
                    return "A"

        match = re.search(rf"\b{letter}\s*(\d{{1,5}})\s*[-/]\s*(\d{{1,8}})\b", texto)
        if match:
            return match.group(1)

    return None
