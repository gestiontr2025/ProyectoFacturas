"""Coordinador del análisis fiscal de un texto ya extraído del PDF.

Este módulo no conoce Gmail, archivos ni proveedores. Su única responsabilidad
es coordinar los extractores fiscales y devolver un resultado coherente.
Separar esta orquestación permite reemplazar o agregar estrategias en el futuro
sin obligar al resto de la aplicación a conocer expresiones regulares.
"""

from __future__ import annotations

from fiscal.analysis_result import FiscalHeaderAnalysis
from fiscal.definitions import is_supported_combination
from fiscal.issue_date import detectar_fecha_emision
from fiscal.letter import detectar_letra_comprobante
from fiscal.number import detectar_numero_comprobante
from fiscal.type_detector import detectar_tipo_comprobante


def analizar_encabezado_fiscal(texto: str) -> FiscalHeaderAnalysis:
    """Analizar tipo, letra, número y fecha mediante una única interfaz.

    La función admite resultados parciales. No inventa una letra ni una fecha
    para completar un documento. En su lugar incorpora advertencias que luego
    pueden mostrarse en un diagnóstico o conservar el archivo en pendientes.
    """

    document_type = detectar_tipo_comprobante(texto)
    fiscal_letter = detectar_letra_comprobante(texto)
    document_number = detectar_numero_comprobante(texto)
    issue_date = detectar_fecha_emision(texto)

    warnings: list[str] = []

    if document_type and fiscal_letter and not is_supported_combination(
        document_type, fiscal_letter
    ):
        warnings.append(
            "La combinación de tipo y letra no pertenece al alcance fiscal "
            "configurado por el proyecto."
        )

    if fiscal_letter and not document_type:
        warnings.append(
            "Se detectó una letra fiscal, pero no fue posible confirmar el "
            "tipo de comprobante."
        )

    if document_number and not document_type:
        warnings.append(
            "Se detectó un número con estructura fiscal, pero no se confirmó "
            "el tipo de comprobante."
        )

    return FiscalHeaderAnalysis(
        document_type=document_type,
        fiscal_letter=fiscal_letter,
        document_number=document_number,
        issue_date=issue_date,
        warnings=tuple(warnings),
    )
