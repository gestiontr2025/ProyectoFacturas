"""Cobertura de familias restantes observadas en _Pendientes."""

from documents import TipoDocumento, clasificar_documento
from invoices.filename_evidence import extraer_evidencia_nombre_archivo
from suppliers.filename_evidence import detectar_identificador_por_nombre


def test_supplier_can_be_resolved_from_known_cuit_in_filename():
    assert (
        detectar_identificador_por_nombre("30711183058_01_0003_00063985.pdf")
        == "sadelar_s_r_l"
    )


def test_receiver_cuit_is_never_used_as_supplier_filename_evidence():
    assert detectar_identificador_por_nombre(
        "30718347463_A-0006-00001163.pdf"
    ) is None


def test_afip_filename_accepts_two_digit_document_code():
    evidence = extraer_evidencia_nombre_archivo(
        "30711183058_01_0003_00063985.pdf"
    )
    assert evidence.tipo_comprobante == "FACTURA"
    assert evidence.letra_comprobante == "A"
    assert evidence.numero_comprobante == "00003-00063985"


def test_timestamp_prefix_does_not_hide_compact_faca():
    evidence = extraer_evidencia_nombre_archivo(
        "2026043000058121FACA000400010187_Orig.pdf"
    )
    assert evidence.tipo_comprobante == "FACTURA"
    assert evidence.letra_comprobante == "A"
    assert evidence.numero_comprobante == "00004-00010187"


def test_venta_a_filename_is_parsed():
    evidence = extraer_evidencia_nombre_archivo("Venta_A00013-00032324.pdf")
    assert evidence.tipo_comprobante == "FACTURA"
    assert evidence.letra_comprobante == "A"
    assert evidence.numero_comprobante == "00013-00032324"


def test_m_facta_filename_is_parsed():
    evidence = extraer_evidencia_nombre_archivo("M-FACTA0006-00006544.pdf")
    assert evidence.tipo_comprobante == "FACTURA"
    assert evidence.letra_comprobante == "A"
    assert evidence.numero_comprobante == "00006-00006544"


def test_flexible_credit_note_filename_is_parsed():
    evidence = extraer_evidencia_nombre_archivo("N CB0001000000768.pdf")
    assert evidence.tipo_comprobante == "NOTA DE CREDITO"
    assert evidence.letra_comprobante == "B"
    assert evidence.numero_comprobante == "00010-00000768"


def test_explicit_payment_receipt_is_archived():
    result = clasificar_documento(
        "",
        "02-07Comprobante de pago de Madero Roof Top S.A a Nestle.pdf",
    )
    assert result.tipo == TipoDocumento.COMPROBANTE_PAGO


def test_explicit_transfer_is_archived():
    result = clasificar_documento("", "Melba transferencia 23-07-2025.pdf")
    assert result.tipo == TipoDocumento.RETENCIONES_TRANSFERENCIAS


def test_explicit_service_payment_is_administrative():
    result = clasificar_documento("", "Pago De Servicios_2026-05-20.pdf")
    assert result.tipo == TipoDocumento.ADMINISTRATIVO
