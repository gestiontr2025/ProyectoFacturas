"""Regresiones descubiertas durante la prueba OCR con comprobantes rasterizados."""

from fiscal.parser import analizar_encabezado_fiscal
from fiscal.type_detector import detectar_tipo_comprobante
from suppliers.ad_hoc import detectar_emisor_no_recurrente


def test_nota_credito_prioriza_su_numero_sobre_factura_asociada():
    texto = """
    CONSTRUCCIONES KAISA S.A.
    CUIT 30-71223344-9 IVA Responsable Inscripto
    NOTA DE CREDITO A
    00009-00000128
    Fecha: 08/08/2026
    Cliente: MADERO ROOF TOP S.A. CUIT 30-71834746-3
    Comprobante asociado: Factura A 00009-00000754
    IVA 21% $ 4.200,00
    CAE 74642345678904
    """
    result = analizar_encabezado_fiscal(texto)
    assert result.document_type == "NOTA DE CREDITO"
    assert result.fiscal_letter == "A"
    assert result.document_number == "00009-00000128"


def test_comprobante_asociado_nunca_es_razon_social():
    texto = """
    CONSTRUCCIONES KAISA S.A.
    CUIT 30-71223344-9 IVA Responsable Inscripto
    NOTA DE CREDITO A
    00009-00000128
    Fecha: 08/08/2026
    Cliente: MADERO ROOF TOP S.A. CUIT 30-71834746-3
    Comprobante asociado: Factura A 00009-00000754
    CAE 74642345678904
    """
    supplier = detectar_emisor_no_recurrente(texto, None)
    assert supplier is not None
    assert supplier["razon_social_canonica"] == "CONSTRUCCIONES KAISA S.A"
    assert supplier["cuit_canonico"] == "30-71223344-9"


def test_cuit_junto_a_madero_se_excluye_aunque_no_sea_el_canonico():
    texto = """
    ORIGINAL
    PANADERIA AKALI S.A.
    Razon Social: PANADERIA AKALI S.A.
    CUIT 30-71824567-9
    FACTURA A 00012-00004567
    Fecha de emision 05/08/2026
    Cliente: MADERO ROOF TOP S.A. CUIT 30-71583474-6
    CAE 74612345678901
    """
    supplier = detectar_emisor_no_recurrente(texto, "30-71583474-6")
    assert supplier is not None
    assert supplier["razon_social_canonica"] == "PANADERIA AKALI S.A"
    assert supplier["cuit_canonico"] == "30-71824567-9"


def test_letra_aislada_ocr_se_acepta_con_numero_fiscal_completo():
    texto = """
    AELIN RAMIREZ
    C
    CUIT 27-33445566-7
    FACTURA
    Nro. 00003-00000991
    Emision 07/08/2026
    MADERO ROOF TOP S.A. CUIT 30-71834746-3
    CAE 74632345678903
    """
    result = analizar_encabezado_fiscal(texto)
    assert result.document_type == "FACTURA"
    assert result.fiscal_letter == "C"
    assert result.document_number == "00003-00000991"


def test_nota_debito_puede_recuperarse_desde_total_debito_si_ocr_pierde_titulo():
    texto = """
    EVENTOS MANON A
    CUIT 27-29887766-5
    Numero: 00015-00000333
    IVA Responsable Inscripto
    09/08/2026
    Receptor MADERO ROOF TOP S.A. CUIT 30-71834746-3
    Neto gravado $ 33.057,85
    IVA 21% $ 6.942,15
    TOTAL DEBITO $ 40.000,00
    CAE 74652345678905
    """
    result = analizar_encabezado_fiscal(texto)
    assert result.document_type == "NOTA DE DEBITO"
    assert result.fiscal_letter == "A"
    assert result.document_number == "00015-00000333"
    assert result.issue_date == "09/08/2026"


def test_no_es_factura_no_convierte_un_remito_en_factura():
    texto = """
    REMITO FLORERIA ZENTREYA
    Razon Social: FLORERIA ZENTREYA
    CUIT 27-40112233-3
    R 00004-00000672
    Fecha de entrega: 10/08/2026
    Destinatario: MADERO ROOF TOP S.A. CUIT 30-71834746-3
    Documento de traslado - NO ES FACTURA
    """
    assert detectar_tipo_comprobante(texto) is None
