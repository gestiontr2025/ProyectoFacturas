"""Regresiones para familias reales descubiertas durante el full scan."""

from invoices.filename_evidence import extraer_evidencia_nombre_archivo
from suppliers.filename_evidence import detectar_identificador_por_nombre
from suppliers.content_evidence import detectar_identificador_por_contenido
import supplier_detector


def test_faca_compacto():
    ev = extraer_evidencia_nombre_archivo("FACA0000200000032.pdf")
    assert ev.tipo_comprobante == "FACTURA"
    assert ev.letra_comprobante == "A"
    assert ev.numero_comprobante == "00002-00000032"


def test_facb_compacto():
    ev = extraer_evidencia_nombre_archivo("FACB0000700207517.pdf")
    assert ev.tipo_comprobante == "FACTURA"
    assert ev.letra_comprobante == "B"
    assert ev.numero_comprobante == "00007-00207517"


def test_factura_arca_descriptiva():
    ev = extraer_evidencia_nombre_archivo("factura_ARCA_A_0022-00001544.pdf")
    assert (ev.tipo_comprobante, ev.letra_comprobante) == ("FACTURA", "A")
    assert ev.numero_comprobante == "00022-00001544"


def test_fcvta():
    ev = extraer_evidencia_nombre_archivo(
        "20260206093009_Comprobante-FCVTA-A-1-12511.pdf"
    )
    assert (ev.tipo_comprobante, ev.letra_comprobante) == ("FACTURA", "A")
    assert ev.numero_comprobante == "00001-00012511"


def test_nota_credito_descriptiva():
    ev = extraer_evidencia_nombre_archivo(
        "Nota de Crédito N° A-00006-00001390.pdf"
    )
    assert ev.tipo_comprobante == "NOTA DE CREDITO"
    assert ev.letra_comprobante == "A"
    assert ev.numero_comprobante == "00006-00001390"


def test_nota_debito_compacta():
    ev = extraer_evidencia_nombre_archivo("N_DA0000200000002.pdf")
    assert ev.tipo_comprobante == "NOTA DE DEBITO"
    assert ev.letra_comprobante == "A"
    assert ev.numero_comprobante == "00002-00000002"


def test_bartoszuk_detected_by_cuit_and_name():
    result = supplier_detector.detectar_proveedor(
        "BARTOSZUK GONZALO ANDRES CUIT 20405472202 MADERO ROOF TOP S.A."
    )
    assert result["proveedor_detectado"] is True
    assert result["identificador"] == "bartoszuk_gonzalo_andres"


def test_don_pacho_detected_despite_pancho_typo():
    result = supplier_detector.detectar_proveedor(
        "ESTABLECIMIENTO DON PANCHO 2024 SRL CUIT 30718771621"
    )
    assert result["proveedor_detectado"] is True
    assert result["identificador"] == "establecimiento_don_pacho_2024"


def test_ivini_signature_identifies_cantine():
    assert detectar_identificador_por_contenido(
        "BANCO GALICIA ALIAS IVINI.GALICIA FACTURA A"
    ) == "cantine_s_r_l"


def test_los_prados_attachment_family():
    assert detectar_identificador_por_nombre(
        "FA_002000042249_20260304_011454_20260304_04_47_10.pdf"
    ) == "frigorifico_los_prados"
