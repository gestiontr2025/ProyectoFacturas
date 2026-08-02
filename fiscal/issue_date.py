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


def detectar_fecha_emision(texto: str) -> Optional[str]:
    """Buscar primero etiquetas explícitas y luego un respaldo fiscal limitado."""
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

    # Solo usamos la primera fecha sin etiqueta cuando el documento ya fue
    # reconocido como comprobante fiscal. Así evitamos tomar fechas de listas,
    # catálogos o comunicaciones comerciales.
    if detectar_tipo_comprobante(texto):
        for valor in re.findall(PATRON_FECHA, texto):
            fecha = _limpiar_fecha(valor)
            if fecha:
                return fecha
    return None
