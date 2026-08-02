"""Extracción y normalización del número de comprobante."""

import re
from typing import Optional

from fiscal.normalization import normalizar_para_busqueda
from fiscal.type_detector import detectar_tipo_comprobante


def _normalizar(punto_venta: str, numero: str) -> str:
    """Aplicar el formato uniforme ``00000-00000000``."""
    return f"{punto_venta.zfill(5)}-{numero.zfill(8)}"


def detectar_numero_comprobante(texto: str) -> Optional[str]:
    """Detectar punto de venta y número usando formatos fiscales frecuentes."""
    texto = normalizar_para_busqueda(texto)
    if not texto:
        return None

    etiqueta = r"(?:NRO\.?|NUMERO|NO\.?)"
    patrones = (
        rf"\b(?:FACTURA|NOTA\s+(?:DE\s+)?CREDITO|NOTA\s+(?:DE\s+)?DEBITO)(?:\s+[ABC])?.{{0,40}}?{etiqueta}\s*[:\-]?\s*(\d{{1,5}})\s*[-/]\s*(\d{{1,8}})",
        rf"\b{etiqueta}\s*[:\-]?\s*(\d{{1,5}})\s*[-/]\s*(\d{{1,8}})",
        r"\b(?:FC|NC|ND)\s*[-_/ ]*[ABC]\s*[-_/ ]*(\d{1,5})\s*[-_/]\s*(\d{1,8})\b",
    )
    for patron in patrones:
        coincidencia = re.search(patron, texto)
        if coincidencia:
            return _normalizar(*coincidencia.groups())

    separado = re.search(
        r"(?:PTO\.?\s*(?:DE\s*)?VTA\.?|PUNTO\s+DE\s+VENTA)\s*[:\-]?\s*(\d{1,5}).{0,150}?(?:NRO\.?|NUMERO|NO\.?)\s*[:\-]?\s*(\d{1,8})",
        texto,
    )
    if separado:
        return _normalizar(*separado.groups())

    if detectar_tipo_comprobante(texto):
        coincidencia = re.search(
            r"\b[ABC]\s+(\d{1,5})\s*[-/]\s*(\d{1,8})\b", texto
        )
        if coincidencia:
            return _normalizar(*coincidencia.groups())
    return None
