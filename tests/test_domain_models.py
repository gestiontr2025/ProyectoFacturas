from pathlib import Path

from models import FiscalDocument, ProcessingResult, ProcessingStatus, Supplier


class LegacyInvoice:
    tipo_comprobante = "NOTA DE CREDITO"
    letra_comprobante = "B"
    numero_comprobante = "00004-00000125"
    fecha_emision = "31/07/2026"
    cuit_emisor = "30-12345678-9"
    razon_social_emisor = "PROVEEDOR SA"
    cuit_receptor = None
    razon_social_receptor = None
    moneda = "ARS"
    subtotal = None
    impuestos = None
    importe_total = None
    cae = None
    vencimiento_cae = None


def test_fiscal_document_adapts_legacy_invoice():
    document = FiscalDocument.from_legacy(LegacyInvoice())
    assert document.fiscal_code == "NCB"
    assert document.point_of_sale == "00004"
    assert document.sequential_number == "00000125"
    assert document.missing_required_fields() == []


def test_fiscal_document_reports_missing_fields_defensively():
    document = FiscalDocument(document_type="FACTURA")
    assert document.missing_required_fields(require_supplier=True) == [
        "fecha de emisión",
        "letra del comprobante",
        "número de comprobante",
        "proveedor",
    ]


def test_supplier_adapts_detector_dictionary_and_prefers_trade_name():
    supplier = Supplier.from_detection_result({
        "proveedor_detectado": True,
        "identificador": "colppy",
        "razon_social_encontrada": "ALL ONLINE SOLUTIONS S. A. U.",
        "nombre_fantasia": "Colppy",
        "cuit_encontrado": "30-71246122-1",
        "nivel_confianza": "alta",
        "puntaje": 11,
    })
    assert supplier.detected is True
    assert supplier.legal_name == "ALL ONLINE SOLUTIONS S. A. U."
    assert supplier.folder_name == "Colppy"


def test_processing_result_exposes_success_state():
    result = ProcessingResult(
        status=ProcessingStatus.ORGANIZED,
        original_path=Path("pending.pdf"),
        final_path=Path("supplier/final.pdf"),
    )
    assert result.successful is True
