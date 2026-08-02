"""Detección defensiva de la fecha de emisión."""

import re
from datetime import datetime
from typing import Optional

from fiscal.normalization import normalizar_para_busqueda
from fiscal.type_detector import detectar_tipo_comprobante

PATRON_FECHA = r"(\d{1,2}[./-]\d{1,2}[./-](?:\d{4}|\d{2}))"


def _limpiar_fecha(valor: str) -> Optional[str]:
    """Validar una fecha y devolverla como ``DD/MM/AAAA``."""
    for formato in ("%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%d/%m/%y", "%d-%m-%y"):
        try:
            return datetime.strptime(valor, formato).strftime("%d/%m/%Y")
        except ValueError:
            continue
    return None


def _detectar_fecha_en_bloque_arca(texto: str) -> Optional[str]:
    """Recuperar la emisión cuando ARCA separa etiquetas y valores.

    En ciertos comprobantes la extracción lineal reúne primero las etiquetas:

        Período desde / hasta / vencimiento / fecha de emisión

    y después entrega cuatro fechas consecutivas. En esa estructura la cuarta
    fecha corresponde a la emisión. La regla exige todo el encabezado fiscal;
    no se aplica a una secuencia arbitraria de fechas.
    """
    patron = (
        r"PERIODO\s+FACTURADO\s+DESDE:.{0,80}?HASTA:.{0,80}?"
        r"FECHA\s+DE\s+VTO\.?\s+PARA\s+EL\s+PAGO:.{0,500}?"
        rf"{PATRON_FECHA}\s+{PATRON_FECHA}\s+{PATRON_FECHA}\s+{PATRON_FECHA}"
    )
    coincidencia = re.search(patron, texto)
    if not coincidencia:
        return None
    return _limpiar_fecha(coincidencia.group(4))


def detectar_fecha_emision(texto: str) -> Optional[str]:
    """Buscar la fecha de emisión de mayor a menor evidencia contextual."""
    texto = normalizar_para_busqueda(texto)
    if not texto:
        return None

    etiquetas = (
        r"FECHA\s+DE\s+EMISION",
        r"FECHA\s+EMISION",
        r"FECHA\s+DEL\s+COMPROBANTE",
        r"FECHA",
    )
    for etiqueta in etiquetas:
        coincidencia = re.search(rf"\b{etiqueta}\b\s*[:\-]?\s*{PATRON_FECHA}", texto)
        if coincidencia:
            fecha = _limpiar_fecha(coincidencia.group(1))
            if fecha:
                return fecha

    fecha_arca = _detectar_fecha_en_bloque_arca(texto)
    if fecha_arca:
        return fecha_arca

    # Solo usamos la primera fecha sin etiqueta cuando el documento ya fue
    # reconocido como comprobante fiscal. Es el último respaldo, porque una
    # fecha sin contexto podría ser un período o un vencimiento.
    if detectar_tipo_comprobante(texto):
        for valor in re.findall(PATRON_FECHA, texto):
            fecha = _limpiar_fecha(valor)
            if fecha:
                return fecha
    return None
