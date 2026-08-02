from pathlib import Path

from documents import TipoDocumento, clasificar_documento
from fiscal.issue_date import detectar_fecha_emision
from invoices.filename_evidence import extraer_evidencia_nombre_archivo
from storage.invoice_date_audit import build_corrected_path


def test_recibo_x_con_referencias_a_facturas_tiene_prioridad_no_fiscal():
    result = clasificar_documento(
        "X RECIBO Documento no válido como factura. Detalle de comprobantes 01A003900126858",
        "RDRC596270_ES_7213114_751325_1628.pdf",
    )
    assert result.tipo is TipoDocumento.REMITO_RECIBO


def test_transferencia_no_se_convierte_en_factura_por_el_concepto():
    result = clasificar_documento(
        "Comprobante de transferencia. Concepto Facturas. Número de operación 123",
        "comprobante.pdf",
    )
    assert result.tipo is TipoDocumento.RETENCIONES_TRANSFERENCIAS


def test_lista_vertical_de_precios_se_reconoce():
    result = clasificar_documento(
        "L I S T A  D E  P R E C I O S  A C T U A L I Z A D A Producto Presentacion Precio",
        "CAHE_20260311.pdf",
    )
    assert result.tipo is TipoDocumento.LISTA_PRECIOS


def test_nombre_sap_fact_a_separa_punto_y_numero():
    evidence = extraer_evidencia_nombre_archivo(
        "V072_CUIT_30504155354_CUIT_30718347463_FACT_A002600360215.pdf"
    )
    assert evidence.tipo_comprobante == "FACTURA"
    assert evidence.letra_comprobante == "A"
    assert evidence.numero_comprobante == "00026-00360215"


def test_fecha_textual_sap_tiene_prioridad_sobre_inicio_actividades():
    text = """
    FACTURA 0026-00360215
    BS.AS., 12 DE MAYO DE 2026
    INICIO DE ACTIVIDADES: 01-06-1979
    Fecha Vto. 22/05/2026
    """
    assert detectar_fecha_emision(text) == "12/05/2026"


def test_fecha_antes_de_factura_resuelve_layout_invertido():
    text = """
    Inicio Actividades: 16/07/1997
    Fecha Vencimiento C.A.E.: 01/05/2026
    21/04/2026
    FACTURA
    Fecha:
    0011 00062463
    """
    assert detectar_fecha_emision(text) == "21/04/2026"


def test_ruta_corregida_preserva_proveedor_y_nombre_fiscal(tmp_path: Path):
    root = tmp_path / "Facturas"
    source = root / "DF_MEGAFRIO_SRL" / "2008" / "09" / (
        "03-09FCA00011-00062463_MADERO_ROOF_TOP_DF_MEGAFRIO_SRL.pdf"
    )
    expected = root / "DF_MEGAFRIO_SRL" / "2026" / "04" / (
        "21-04FCA00011-00062463_MADERO_ROOF_TOP_DF_MEGAFRIO_SRL.pdf"
    )
    assert build_corrected_path(root, source, "21/04/2026") == expected
