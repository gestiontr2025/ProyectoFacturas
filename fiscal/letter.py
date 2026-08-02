"""Detección de la letra fiscal A, B o C."""

import re
from typing import Optional

from fiscal.normalization import normalizar_para_busqueda
from fiscal.type_detector import detectar_tipo_comprobante

LETRAS_VALIDAS = {"A", "B", "C"}


def detectar_letra_comprobante(texto: str) -> Optional[str]:
    """Detectar la letra únicamente cuando existe contexto fiscal suficiente.

    Una letra aislada no es evidencia: podría pertenecer a una dirección o a un
    producto. Por eso cada patrón exige una etiqueta fiscal, un código compacto
    o la combinación letra+número dentro de un documento fiscal reconocido.
    """
    texto = normalizar_para_busqueda(texto)
    if not texto:
        return None

    patrones = (
        r"\b(?:FACTURA|NOTA\s+(?:DE\s+)?CREDITO|NOTA\s+(?:DE\s+)?DEBITO)\s*[-:]?\s*([ABC])\b",
        r"\b(?:FC|NC|ND)\s*[-_/ ]*([ABC])\b",
        r"\bLETRA\s*[:\-]?\s*([ABC])\b",
    )
    for patron in patrones:
        coincidencia = re.search(patron, texto)
        if coincidencia:
            return coincidencia.group(1)

    if detectar_tipo_comprobante(texto):
        coincidencia = re.search(
            r"\b([ABC])\s+(\d{1,5})\s*[-/]\s*(\d{1,8})\b", texto
        )
        if coincidencia:
            return coincidencia.group(1)
    return None
