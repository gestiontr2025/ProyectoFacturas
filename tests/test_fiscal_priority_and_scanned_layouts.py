"""Regresiones para comprobantes fiscales que compiten con otras categorías."""

from documents import TipoDocumento, clasificar_documento
import invoice_parser
from suppliers.issuer_identity import extraer_identidad_emisor


CATENA_LEGACY_TEXT = """
A
Codigo N 01
FACTURA 0056 - 00562701
06 02 2026
18/08/2003
30-50258442-8
INSCRIPTO 30-71834746-3
PERCEP. IB CABA RES.296/2019
PERCEP.IVA 3%
FECHA DE VENCIMIENTO: 16/02/2026
C.A.E.: 86062827317393
LA PRESENTE FACTURA NO ES COMPROBANTE DE PAGO
TOTAL A PAGAR $ 387297.53
"""


CONSORCIO_OCR_TEXT = """
CONSORCIO
LIQUIDACION DE GASTOS COMUNES
COPROPIETARIOS
N°.00001-00005591
30 06 2026
FECHA:
CUIT N°:
30-70772277-7
Ing. Brutos:
No Responsable
Fecha de Inicio de Actividades:
01/08/2001
IVA - Responsable Inscripto
Senor Consorcista:
MADERO ROOF TOP S.A.
Emitir cheques a la orden de:
CONSORCIO DE COP COSSETTINI
FA_"A"_0001-00005591
IVA 21% 607426.83
IVA 27% 233628.55
TOTAL 4997143.98
"""


def test_catena_no_es_comprobante_de_pago_sigue_siendo_factura():
    resultado = clasificar_documento(CATENA_LEGACY_TEXT, "Factura_0056-00562701.pdf")
    assert resultado.tipo is TipoDocumento.FACTURA
    assert resultado.puntaje_factura >= 10


def test_parser_legacy_catena_recupera_identidad_fiscal_completa():
    datos = invoice_parser.extraer_datos_factura(CATENA_LEGACY_TEXT).datos
    assert datos.tipo_comprobante == "FACTURA"
    assert datos.letra_comprobante == "A"
    assert datos.numero_comprobante == "00056-00562701"
    assert datos.fecha_emision == "06/02/2026"


def test_liquidacion_consorcio_con_evidencia_fiscal_prioriza_factura():
    resultado = clasificar_documento(CONSORCIO_OCR_TEXT, "CCF_000480.pdf")
    assert resultado.tipo is TipoDocumento.FACTURA
    assert resultado.puntaje_factura >= 10


def test_parser_liquidacion_consorcio_recupera_factura_a():
    datos = invoice_parser.extraer_datos_factura(CONSORCIO_OCR_TEXT).datos
    assert datos.tipo_comprobante == "FACTURA"
    assert datos.letra_comprobante == "A"
    assert datos.numero_comprobante == "00001-00005591"
    assert datos.fecha_emision == "30/06/2026"
    assert datos.cuit_emisor == "30-70772277-7"


def test_scoring_emisor_consorcio_prefiere_denominacion_explicita():
    identidad = extraer_identidad_emisor(CONSORCIO_OCR_TEXT, "30-70772277-7")
    assert identidad is not None
    assert identidad.cuit == "30-70772277-7"
    assert identidad.legal_name == "CONSORCIO DE COP COSSETTINI"
    assert "denominacion_consorcio_explicita" in identidad.evidence


def test_expensas_sin_palabra_factura_con_estructura_fiscal_sigue_flujo_factura():
    texto = """
    CONSORCIO
    LIQUIDACION DE GASTOS COMUNES
    N°. 00001- 00005530
    A
    FECHA: 28 02 2026
    Venc.10/03/2026
    CUIT N°: 30-70772277-7
    IVA - Responsable Inscripto
    MADERO ROOF TOP S.A.
    CONSORCIO DE COP COSSETTINI 703/787
    IVA 21% 488083.79
    IVA 27% 198321.15
    TOTAL 4256561.27
    """
    clasificacion = clasificar_documento(texto, "CCF_000345_expensas.pdf")
    assert clasificacion.tipo is TipoDocumento.FACTURA

    datos = invoice_parser.extraer_datos_factura(texto).datos
    assert datos.tipo_comprobante == "FACTURA"
    assert datos.letra_comprobante == "A"
    assert datos.numero_comprobante == "00001-00005530"
    assert datos.fecha_emision == "28/02/2026"


def test_recibo_explicito_no_se_convierte_en_factura_por_facturas_imputadas():
    texto = """
    RECIBO OFICIAL
    N° Recibo: 00001-00006673
    CUIT 30-69757899-0
    MADERO ROOF TOP S.A.
    FACTURA A00008-00001348
    IMPORTE 6650160.00
    TOTAL 6650160.00
    """
    resultado = clasificar_documento(texto, "CCF_000315.pdf")
    assert resultado.tipo is TipoDocumento.REMITO_RECIBO


def test_fecha_ocr_repara_anio_con_vencimiento_coherente():
    texto = """
    LIQUIDACION DE GASTOS COMUNES
    N°. 00001-00005606
    A
    FECHA: 31 07 2028
    Venc.10/08/2026
    CUIT N°: 30-70772277-7
    IVA 21% 100.00
    IVA 27% 200.00
    """
    datos = invoice_parser.extraer_datos_factura(texto).datos
    assert datos.fecha_emision == "31/07/2026"


def test_vencimiento_no_se_usa_como_fecha_de_emision_si_hay_fecha_valida_posterior():
    texto = """
    LIQUIDACION DE GASTOS COMUNES
    N°. 00001-00005561
    A
    FECHA; 3° 04 2020
    Venc.10/05/2026
    CUIT N°: 30-70772277-7
    IVA 21% 100.00
    IVA 27% 200.00
    DETALLES DE GASTOS Y PROVISIONES PRORRATEABLES
    30/04/2026
    """
    datos = invoice_parser.extraer_datos_factura(texto).datos
    assert datos.fecha_emision == "30/04/2026"


def test_nombre_consorcio_descarta_numeracion_de_domicilio():
    texto = """
    LIQUIDACION DE GASTOS COMUNES
    N°. 00001-00005530
    A
    CUIT N°: 30-70772277-7
    MADERO ROOF TOP S.A.
    Emitir cheques a la orden de: CONSORCIO DE COP COSSETTINI 703/787
    IVA 21% 100.00
    IVA 27% 200.00
    """
    identidad = extraer_identidad_emisor(texto, "30-70772277-7")
    assert identidad is not None
    assert identidad.legal_name == "CONSORCIO DE COP COSSETTINI"
