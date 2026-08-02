"""Motor modular para interpretar comprobantes fiscales argentinos.

El paquete separa cuatro responsabilidades que antes estaban mezcladas dentro
``invoice_parser.py``: tipo de comprobante, letra fiscal, número y fecha.

La API pública se mantiene pequeña para que el resto del proyecto no dependa de
las expresiones regulares internas.
"""

from fiscal.issue_date import detectar_fecha_emision
from fiscal.letter import detectar_letra_comprobante
from fiscal.number import detectar_numero_comprobante
from fiscal.type_detector import detectar_tipo_comprobante

__all__ = [
    "detectar_fecha_emision",
    "detectar_letra_comprobante",
    "detectar_numero_comprobante",
    "detectar_tipo_comprobante",
]
