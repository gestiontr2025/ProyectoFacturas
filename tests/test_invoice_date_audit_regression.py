"""Regresiones de fecha compartidas por parser y auditor."""

from fiscal.issue_date import detectar_fecha_emision


def test_identidad_fiscal_seguida_de_fecha_gana_sobre_fvto():
    texto = (
        "F A C T U R A B 00021-00001477 08 07 25 "
        "CAE: 75271643145619 F.VTO: 18/07/2025"
    )

    assert detectar_fecha_emision(
        texto, contexto_fiscal_confirmado=True
    ) == "08/07/2025"


def test_pdf_con_un_caracter_por_linea_no_confunde_fvto_con_emision():
    texto = "\n".join(
        list(
            "FACTURAB00021-00001477080725006"
            "SantiagoScavuzzoCAE:75271643145619F.VTO:18/07/2025"
        )
    )

    assert detectar_fecha_emision(
        texto, contexto_fiscal_confirmado=True
    ) == "08/07/2025"
