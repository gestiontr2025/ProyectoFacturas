"""Especificación del coordinador fiscal y sus definiciones centrales."""

import pytest

from fiscal import (
    SUPPORTED_LETTERS,
    analizar_encabezado_fiscal,
    build_fiscal_code,
    is_supported_combination,
)


@pytest.mark.parametrize(
    ("title", "expected_type", "expected_letter", "expected_code"),
    [
        ("FACTURA A", "FACTURA", "A", "FCA"),
        ("FACTURA B", "FACTURA", "B", "FCB"),
        ("FACTURA C", "FACTURA", "C", "FCC"),
        ("NOTA DE CREDITO A", "NOTA DE CREDITO", "A", "NCA"),
        ("NOTA DE CREDITO B", "NOTA DE CREDITO", "B", "NCB"),
        ("NOTA DE CREDITO C", "NOTA DE CREDITO", "C", "NCC"),
        ("NOTA DE DEBITO A", "NOTA DE DEBITO", "A", "NDA"),
        ("NOTA DE DEBITO B", "NOTA DE DEBITO", "B", "NDB"),
        ("NOTA DE DEBITO C", "NOTA DE DEBITO", "C", "NDC"),
    ],
)
def test_coordinator_supports_all_nine_priority_combinations(
    title, expected_type, expected_letter, expected_code
):
    analysis = analizar_encabezado_fiscal(
        f"{title}\nNro. 0004-00000125\nFecha: 01/08/2026"
    )

    assert analysis.document_type == expected_type
    assert analysis.fiscal_letter == expected_letter
    assert analysis.document_number == "00004-00000125"
    assert analysis.issue_date == "01/08/2026"
    assert analysis.fiscal_code == expected_code
    assert analysis.supported_combination is True
    assert analysis.warnings == ()


def test_compact_abbreviations_keep_type_and_letter_separate():
    cases = {
        "FCA Nro 1-15 Fecha 02/08/2026": ("FACTURA", "A", "FCA"),
        "FCB Nro 2-16 Fecha 02/08/2026": ("FACTURA", "B", "FCB"),
        "FCC Nro 3-17 Fecha 02/08/2026": ("FACTURA", "C", "FCC"),
        "NCA Nro 4-18 Fecha 02/08/2026": ("NOTA DE CREDITO", "A", "NCA"),
        "NDB Nro 5-19 Fecha 02/08/2026": ("NOTA DE DEBITO", "B", "NDB"),
    }

    for text, expected in cases.items():
        analysis = analizar_encabezado_fiscal(text)
        assert (
            analysis.document_type,
            analysis.fiscal_letter,
            analysis.fiscal_code,
        ) == expected


def test_supported_letters_are_explicit_and_not_inferred_from_arbitrary_text():
    assert SUPPORTED_LETTERS == ("A", "B", "C")
    assert build_fiscal_code("FACTURA", "B") == "FCB"
    assert build_fiscal_code("NOTA DE CREDITO", "C") == "NCC"
    assert is_supported_combination("NOTA DE DEBITO", "A") is True
    assert build_fiscal_code("FACTURA", "X") is None
    assert analizar_encabezado_fiscal("Piso 4 A, Buenos Aires").fiscal_letter is None
