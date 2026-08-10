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


def test_dba_fecha_antes_de_etiqueta_gana_sobre_inicio_actividad():
    texto = """
    A
    06/08/2026 Fecha:
    Nro: 00013-00189814
    Distribuidora de Bebidas SRL
    CUIT: 30-70942442-0
    INICIO ACTIV.:
    01/04/2006
    FACTURA
    CAE: 86327172503529
    16/08/2026 Fecha Vencimiento CAE:
    """

    assert detectar_fecha_emision(
        texto, contexto_fiscal_confirmado=True
    ) == "06/08/2026"
