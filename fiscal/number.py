"""Extracción y normalización del número de comprobante fiscal."""

import re
from typing import Optional

from fiscal.normalization import normalizar_para_busqueda
from fiscal.type_detector import detectar_tipo_comprobante


def _normalizar(punto_venta: str, numero: str) -> str:
    """Aplicar el formato uniforme ``00000-00000000``."""
    return f"{punto_venta.zfill(5)}-{numero.zfill(8)}"


def detectar_numero_comprobante(texto: str) -> Optional[str]:
    """Detectar punto de venta y número usando formatos fiscales frecuentes.

    Los extractores de PDF no siempre conservan la disposición visual. Un
    comprobante que visualmente muestra dos columnas puede convertirse en:

        Punto de Venta: 00002 Comp. Nro: 00000308

    Por eso se reconocen tanto números unidos por guion como campos separados.
    """
    texto = normalizar_para_busqueda(texto)
    if not texto:
        return None

    etiqueta_numero = r"(?:NRO\.?|NUMERO|NO\.?)"
    etiqueta_comprobante = rf"(?:COMP(?:ROBANTE)?\.?\s*)?{etiqueta_numero}"

    patrones = (
        rf"\b(?:FACTURA|NOTA\s+(?:DE\s+)?CREDITO|NOTA\s+(?:DE\s+)?DEBITO)(?:\s+[ABC])?.{{0,40}}?{etiqueta_comprobante}\s*[:\-]?\s*(\d{{1,5}})\s*[-/]\s*(\d{{1,8}})",
        rf"\b{etiqueta_comprobante}\s*[:\-]?\s*(\d{{1,5}})\s*[-/]\s*(\d{{1,8}})",
        r"\b(?:FC|NC|ND)\s*[-_/ ]*[ABC]\s*[-_/ ]*(\d{1,5})\s*[-_/]\s*(\d{1,8})\b",
    )
    for patron in patrones:
        coincidencia = re.search(patron, texto)
        if coincidencia:
            return _normalizar(*coincidencia.groups())

    # Algunos generadores dibujan primero las dos etiquetas y después sus
    # valores. ``pypdf`` puede convertir esa disposición visual en:
    #
    #     PUNTO DE VENTA: COMP. NRO: 00002 00000308
    #
    # Aunque el orden textual resulte extraño, ambos valores siguen asociados
    # a etiquetas fiscales inequívocas, por lo que la extracción es segura.
    etiquetas_antes_de_valores = re.search(
        rf"(?:PTO\.?\s*(?:DE\s*)?VTA\.?|PUNTO\s+DE\s+VENTA)\s*[:\-]?\s*{etiqueta_comprobante}\s*[:\-]?\s*(\d{{1,5}})\s+(\d{{1,8}})",
        texto,
    )
    if etiquetas_antes_de_valores:
        return _normalizar(*etiquetas_antes_de_valores.groups())

    # Formato con campos separados, muy habitual en comprobantes ARCA y
    # Colppy. La ventana de 180 caracteres tolera saltos de línea y campos
    # intermedios sin recorrer todo el documento y capturar números ajenos.
    separado = re.search(
        rf"(?:PTO\.?\s*(?:DE\s*)?VTA\.?|PUNTO\s+DE\s+VENTA)\s*[:\-]?\s*(\d{{1,5}}).{{0,180}}?{etiqueta_comprobante}\s*[:\-]?\s*(\d{{1,8}})",
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
