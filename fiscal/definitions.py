"""Definiciones centrales del dominio fiscal argentino soportado.

Este módulo es la fuente única para las combinaciones de comprobante que el
proyecto considera organizables. Mantener estas reglas en un solo lugar evita
que distintos extractores terminen aceptando letras o códigos incompatibles.

Alcance actual
--------------
El proyecto organiza las nueve combinaciones prioritarias solicitadas:

* Facturas A, B y C.
* Notas de crédito A, B y C.
* Notas de débito A, B y C.

Agregar una nueva letra o familia en el futuro deberá comenzar aquí y estar
acompañado por pruebas. De esa forma el cambio será deliberado y no una
consecuencia accidental de una expresión regular demasiado permisiva.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class FiscalDocumentDefinition:
    """Describir una familia fiscal sin incluir datos de un documento real."""

    canonical_name: str
    filename_prefix: str
    textual_aliases: tuple[str, ...]
    compact_prefixes: tuple[str, ...]


SUPPORTED_LETTERS: Final[tuple[str, ...]] = ("A", "B", "C")

DOCUMENT_DEFINITIONS: Final[tuple[FiscalDocumentDefinition, ...]] = (
    FiscalDocumentDefinition(
        canonical_name="NOTA DE CREDITO",
        filename_prefix="NC",
        textual_aliases=("NOTA DE CREDITO", "NOTA CREDITO"),
        compact_prefixes=("NC",),
    ),
    FiscalDocumentDefinition(
        canonical_name="NOTA DE DEBITO",
        filename_prefix="ND",
        textual_aliases=("NOTA DE DEBITO", "NOTA DEBITO"),
        compact_prefixes=("ND",),
    ),
    FiscalDocumentDefinition(
        canonical_name="FACTURA",
        filename_prefix="FC",
        textual_aliases=("FACTURA",),
        compact_prefixes=("FC", "FAC"),
    ),
)

DEFINITION_BY_NAME: Final[dict[str, FiscalDocumentDefinition]] = {
    definition.canonical_name: definition for definition in DOCUMENT_DEFINITIONS
}

# Códigos AFIP/ARCA correspondientes a las nueve combinaciones prioritarias.
# Se centralizan aquí para que la detección por contenido y por nombre de
# archivo compartan exactamente el mismo conocimiento de dominio.
AFIP_CODE_TO_TYPE_AND_LETTER: Final[dict[int, tuple[str, str]]] = {
    1: ("FACTURA", "A"),
    2: ("NOTA DE DEBITO", "A"),
    3: ("NOTA DE CREDITO", "A"),
    6: ("FACTURA", "B"),
    7: ("NOTA DE DEBITO", "B"),
    8: ("NOTA DE CREDITO", "B"),
    11: ("FACTURA", "C"),
    12: ("NOTA DE DEBITO", "C"),
    13: ("NOTA DE CREDITO", "C"),
}

TYPE_AND_LETTER_TO_AFIP_CODE: Final[dict[tuple[str, str], int]] = {
    value: code for code, value in AFIP_CODE_TO_TYPE_AND_LETTER.items()
}


def is_supported_combination(document_type: str | None, letter: str | None) -> bool:
    """Indicar si tipo y letra forman una combinación fiscal soportada."""

    if not document_type or not letter:
        return False
    return (
        document_type.strip().upper() in DEFINITION_BY_NAME
        and letter.strip().upper() in SUPPORTED_LETTERS
    )


def build_fiscal_code(document_type: str | None, letter: str | None) -> str | None:
    """Construir ``FCA``, ``NCB`` o ``NDC`` desde valores canónicos."""

    if not is_supported_combination(document_type, letter):
        return None
    definition = DEFINITION_BY_NAME[document_type.strip().upper()]
    return f"{definition.filename_prefix}{letter.strip().upper()}"
