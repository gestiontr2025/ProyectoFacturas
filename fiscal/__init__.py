"""API pública del motor fiscal modular.

El resto del proyecto debe importar desde este paquete y no desde los módulos
internos. Así las expresiones regulares pueden evolucionar sin propagar cambios
por toda la aplicación.
"""

from fiscal.analysis_result import FiscalHeaderAnalysis
from fiscal.definitions import (
    AFIP_CODE_TO_TYPE_AND_LETTER,
    DOCUMENT_DEFINITIONS,
    SUPPORTED_LETTERS,
    build_fiscal_code,
    is_supported_combination,
)
from fiscal.issue_date import detectar_fecha_emision, detectar_fecha_emision_para_auditoria
from fiscal.letter import detectar_letra_comprobante
from fiscal.number import detectar_numero_comprobante
from fiscal.parser import analizar_encabezado_fiscal
from fiscal.type_detector import detectar_tipo_comprobante

__all__ = [
    "AFIP_CODE_TO_TYPE_AND_LETTER",
    "DOCUMENT_DEFINITIONS",
    "FiscalHeaderAnalysis",
    "SUPPORTED_LETTERS",
    "analizar_encabezado_fiscal",
    "build_fiscal_code",
    "detectar_fecha_emision",
    "detectar_fecha_emision_para_auditoria",
    "detectar_letra_comprobante",
    "detectar_numero_comprobante",
    "detectar_tipo_comprobante",
    "is_supported_combination",
]
