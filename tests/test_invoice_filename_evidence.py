"""Pruebas del respaldo basado en nombres de archivos reales."""

from invoices.filename_evidence import extraer_evidencia_nombre_archivo


def test_nombre_arta_con_codigo_afip_011():
    evidencia = extraer_evidencia_nombre_archivo(
        "27305950136_011_00004_00000375.pdf"
    )
    assert evidencia.letra_comprobante == "C"
    assert evidencia.numero_comprobante == "00004-00000375"


def test_nombre_fc_a_con_numero():
    evidencia = extraer_evidencia_nombre_archivo(
        "FC A 0003-00025066 MADERO ROOF TOP SA.pdf"
    )
    assert evidencia.letra_comprobante == "A"
    assert evidencia.numero_comprobante == "00003-00025066"


def test_nombre_fa_a_con_numero():
    evidencia = extraer_evidencia_nombre_archivo("FA-A 00040-00069092.pdf")
    assert evidencia.letra_comprobante == "A"
    assert evidencia.numero_comprobante == "00040-00069092"


def test_nombre_factura_sin_letra_no_inventa_letra():
    evidencia = extraer_evidencia_nombre_archivo("Factura 0004-00219487.pdf")
    assert evidencia.letra_comprobante is None
    assert evidencia.numero_comprobante == "00004-00219487"
