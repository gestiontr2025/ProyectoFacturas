from pdf_reader import _seleccionar_mejor_ocr
from suppliers.issuer_identity import extraer_identidad_emisor
from fiscal.parser import analizar_encabezado_fiscal


def test_fusion_ocr_combina_cabecera_fiscal_e_identidad_del_emisor():
    fiscal = """
NOTA DE DEBITO B
Fecha: 09/08/2026
Numero del comprobante
00015-00000333
RECEPTOR
MADERO ROOF TOP S.A. - 30-71583474-6
IVA 21% $ 6.942,15
TOTAL DEBITO $ 40.000,00
"""
    issuer = """
EVENTOS MANON
CUIT 27-29887766-5
NOTA DE DEBITO
MADERO ROOF TOP S.A. 30-71583474-6
"""

    metodo, texto, puntaje = _seleccionar_mejor_ocr(
        [("tesseract_cli_psm4", fiscal), ("tesseract_cli_psm11", issuer)]
    )

    assert metodo.startswith("fusion_ocr[")
    assert puntaje > 0
    header = analizar_encabezado_fiscal(texto)
    identity = extraer_identidad_emisor(texto)
    assert header.document_type == "NOTA DE DEBITO"
    assert header.fiscal_letter == "B"
    assert header.document_number == "00015-00000333"
    assert header.issue_date == "09/08/2026"
    assert identity is not None
    assert identity.legal_name == "EVENTOS MANON"
    assert identity.cuit == "27-29887766-5"


def test_fusion_ocr_no_reemplaza_tipo_letra_ni_numero_ya_confiables():
    base = """
FACTURA B
Fecha de emision: 06/08/2026
Punto de venta 00007
Comprobante Nro 00001842
MADERO ROOF TOP S.A. CUIT RECEPTOR: 30-71583474-6
IVA Responsable Inscripto
IVA 21% 10.00
CAE 74622345678902
TOTAL 100000
"""
    secondary = """
ARCHERON HERMANAS S.R.L.
CUIT EMISOR: 30-70998877-4
FACTURA A
Numero: 00099-99999999
"""

    metodo, texto, _puntaje = _seleccionar_mejor_ocr(
        [("base", base), ("secondary", secondary)]
    )
    header = analizar_encabezado_fiscal(texto)
    identity = extraer_identidad_emisor(texto)

    assert header.document_type == "FACTURA"
    assert header.fiscal_letter == "B"
    assert header.document_number == "00007-00001842"
    assert identity is not None
    assert identity.legal_name == "ARCHERON HERMANAS S.R.L"


def test_fusion_ocr_no_acepta_identidad_con_cuit_invalido():
    fiscal = """
NOTA DE DEBITO B
Fecha: 09/08/2026
Numero: 00015-00000333
"""
    bad_issuer = """
EVENTOS MANON
CUIT 27-20887766-5
"""

    metodo, texto, _puntaje = _seleccionar_mejor_ocr(
        [("fiscal", fiscal), ("bad", bad_issuer)]
    )

    assert not metodo.startswith("fusion_ocr[")
    assert extraer_identidad_emisor(texto) is None
