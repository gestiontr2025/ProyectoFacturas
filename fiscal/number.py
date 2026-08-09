"""Extracción y normalización del número de comprobante fiscal."""

import re
from typing import Optional

from fiscal.normalization import normalizar_para_busqueda
from fiscal.type_detector import detectar_tipo_comprobante


def _normalizar(punto_venta: str, numero: str) -> str:
    """Aplicar el formato uniforme ``00000-00000000``."""
    return f"{punto_venta.zfill(5)}-{numero.zfill(8)}"


def _numero_principal_de_nota(texto: str, tipo: str) -> Optional[str]:
    """Buscar el número propio de una NC/ND antes de referencias asociadas.

    Una nota puede incluir ``Comprobante asociado: Factura A ...``. Ese número
    pertenece al documento referenciado y nunca debe reemplazar al número de la
    nota actual. Buscamos primero una pareja fiscal en la sección que nace en el
    título de la nota y termina antes de cualquier rótulo de asociación.
    """
    title = (
        r"NOTA\s+(?:DE\s+)?CREDITO"
        if tipo == "NOTA DE CREDITO"
        else r"NOTA\s+(?:DE\s+)?DEBITO"
    )
    match = re.search(title, texto)
    if not match:
        return None

    tail = texto[match.end(): match.end() + 320]
    tail = re.split(
        r"\b(?:COMPROBANTE|FACTURA|NOTA)\s+(?:ASOCIAD[AO]|RELACIONAD[AO]|ORIGINAL)\b|"
        r"\b(?:DOCUMENTO|REFERENCIA)\s+(?:ASOCIAD[AO]|RELACIONAD[AO])\b",
        tail,
        maxsplit=1,
    )[0]

    labeled = re.search(
        r"\b(?:NRO\.?|NUMERO|NO\.?)(?:\s+DEL\s+COMPROBANTE|\s+DE\s+ESTA\s+NOTA\s+DE\s+(?:CREDITO|DEBITO))?"
        r"\s*[:\-]?\s*(\d{1,5})\s*[-/]\s*(\d{1,8})\b",
        tail,
    )
    if labeled:
        return _normalizar(*labeled.groups())

    for own in re.finditer(r"\b(?:[ABC]\s*)?(\d{1,5})\s*[-/]\s*(\d{4,8})\b", tail):
        context = tail[max(0, own.start() - 32):own.start()]
        if re.search(r"\b(?:CUIT|FECHA|VENC|VTO)\b", context):
            continue
        return _normalizar(*own.groups())
    return None


def detectar_numero_comprobante(texto: str) -> Optional[str]:
    """Detectar punto de venta y número usando formatos fiscales frecuentes."""
    texto = normalizar_para_busqueda(texto)
    if not texto:
        return None

    tipo = detectar_tipo_comprobante(texto)
    etiqueta_numero = r"(?:NRO\.?|NUMERO|NO\.?)"
    etiqueta_comprobante = rf"(?:COMP(?:ROBANTE)?\.?\s*)?{etiqueta_numero}"

    # En notas, el número del documento actual tiene prioridad absoluta sobre
    # cualquier factura/nota citada como comprobante asociado.
    if tipo in {"NOTA DE CREDITO", "NOTA DE DEBITO"}:
        principal = _numero_principal_de_nota(texto, tipo)
        if principal:
            return principal

    legacy_factura = re.search(r"\bFACTURA\s+(\d{1,5})\s*[-/]\s*(\d{1,8})\b", texto)
    if legacy_factura:
        return _normalizar(*legacy_factura.groups())

    legacy_fa = re.search(
        r"\bFA\s*[-_/\"' ]*[ABC]\s*[-_/\"' ]*(\d{1,5})\s*[-/]\s*(\d{1,8})\b",
        texto,
    )
    if legacy_fa:
        return _normalizar(*legacy_fa.groups())

    patrones = (
        rf"\b(?:FACTURA|NOTA\s+(?:DE\s+)?CREDITO|NOTA\s+(?:DE\s+)?DEBITO)(?:\s+[ABC])?.{{0,40}}?{etiqueta_comprobante}\s*[:\-]?\s*(\d{{1,5}})\s*[-/]\s*(\d{{1,8}})",
        rf"\b{etiqueta_comprobante}\s*[:\-]?\s*(\d{{1,5}})\s*[-/]\s*(\d{{1,8}})",
        r"\b(?:FC|NC|ND)\s*[-_/ ]*[ABC]\s*[-_/ ]*(\d{1,5})\s*[-_/]\s*(\d{1,8})\b",
    )
    for patron in patrones:
        coincidencia = re.search(patron, texto)
        if coincidencia:
            return _normalizar(*coincidencia.groups())

    punto_y_comprobante = re.search(
        r"(?:PTO\.?\s*(?:DE\s*)?VTA\.?|PUNTO\s+DE\s+VENTA)\s*[:\-]?\s*(\d{1,5})"
        r".{0,100}?\bCOMP(?:ROBANTE)?(?:\s+NRO\.?)?\s*[:\-]?\s*(\d{1,8})\b",
        texto,
    )
    if punto_y_comprobante:
        return _normalizar(*punto_y_comprobante.groups())

    etiquetas_antes_de_valores = re.search(
        rf"(?:PTO\.?\s*(?:DE\s*)?VTA\.?|PUNTO\s+DE\s+VENTA)\s*[:\-]?\s*{etiqueta_comprobante}\s*[:\-]?\s*(\d{{1,5}})\s+(\d{{1,8}})",
        texto,
    )
    if etiquetas_antes_de_valores:
        return _normalizar(*etiquetas_antes_de_valores.groups())

    separado = re.search(
        rf"(?:PTO\.?\s*(?:DE\s*)?VTA\.?|PUNTO\s+DE\s+VENTA)\s*[:\-]?\s*(\d{{1,5}}).{{0,180}}?{etiqueta_comprobante}\s*[:\-]?\s*(\d{{1,8}})",
        texto,
    )
    if separado:
        return _normalizar(*separado.groups())

    # Un número precedido por la etiqueta genérica puede aparecer sin la
    # palabra "Comp." (p. ej. ``Numero: 00015-00000333``).
    numero_etiquetado = re.search(
        rf"\b{etiqueta_numero}\s*[:\-]?\s*(\d{{1,5}})\s*[-/]\s*(\d{{1,8}})\b",
        texto,
    )
    if numero_etiquetado:
        return _normalizar(*numero_etiquetado.groups())

    # El formato letra+número compacto se reserva para FACTURA. En una NC/ND
    # podría ser la factura asociada y provocar exactamente el error que esta
    # capa intenta evitar.
    if tipo == "FACTURA":
        coincidencia = re.search(r"\b[ABC]\s*(\d{1,5})\s*[-/]\s*(\d{1,8})\b", texto)
        if coincidencia:
            return _normalizar(*coincidencia.groups())

    return None
