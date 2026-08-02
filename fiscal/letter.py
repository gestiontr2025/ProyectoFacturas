"""Detección defensiva de la letra fiscal A, B o C.

La lista de letras y la relación con códigos AFIP/ARCA viven en
:mod:`fiscal.definitions`. Este módulo se limita a reunir evidencias de texto.
"""

import re
from typing import Optional

from fiscal.definitions import AFIP_CODE_TO_TYPE_AND_LETTER, SUPPORTED_LETTERS
from fiscal.normalization import normalizar_para_busqueda
from fiscal.type_detector import detectar_tipo_comprobante

_LETTER_CLASS = "".join(SUPPORTED_LETTERS)


def _detectar_por_codigo_arca(texto: str, tipo: str) -> Optional[str]:
    """Inferir la letra desde ``COD`` solo cuando el tipo ya es conocido."""

    for match in re.finditer(r"(?:COD(?:IGO)?|TIPO)\.?\s*[:\-]?\s*0*(\d{1,3})\b", texto):
        mapping = AFIP_CODE_TO_TYPE_AND_LETTER.get(int(match.group(1)))
        if mapping and mapping[0] == tipo:
            return mapping[1]
    return None


def detectar_letra_comprobante(texto: str) -> Optional[str]:
    """Detectar A, B o C únicamente con contexto fiscal suficiente.

    Nunca se acepta una letra aislada. En una factura real una ``A`` puede ser
    parte de una dirección, un piso o una descripción; exigir contexto fiscal
    reduce falsos positivos y evita organizar documentos bajo una letra falsa.
    """

    texto = normalizar_para_busqueda(texto)
    if not texto:
        return None

    tipo = detectar_tipo_comprobante(texto)
    letter = rf"([{_LETTER_CLASS}])"

    patterns = (
        rf"\b(?:FACTURA|NOTA\s+(?:DE\s+)?CREDITO|NOTA\s+(?:DE\s+)?DEBITO)\s*[-:]?\s*{letter}\b",
        rf"\b{letter}\s+(?:COD(?:IGO)?\.?\s*0*\d{{1,3}}\s+)?(?:FACTURA|NOTA\s+(?:DE\s+)?CREDITO|NOTA\s+(?:DE\s+)?DEBITO)\b",
        rf"\b(?:FC|FAC|NC|ND)\s*[-_/ ]*{letter}\b",
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

        match = re.search(
            rf"\b{letter}\s+(\d{{1,5}})\s*[-/]\s*(\d{{1,8}})\b", texto
        )
        if match:
            return match.group(1)

    return None
