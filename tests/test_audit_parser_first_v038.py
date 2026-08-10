from pathlib import Path

import pdf_reader
from storage.invoice_date_audit import audit_organized_invoice_dates


def test_auditoria_de_fechas_desactiva_ocr(monkeypatch, tmp_path):
    root = tmp_path / "Facturas"
    source = root / "DBA" / "2006" / "04" / (
        "01-04FCA00013-00189814_MADERO_ROOF_TOP_DISTRIBUIDORA_DE_BEBIDAS_SRL.pdf"
    )
    source.parent.mkdir(parents=True)
    source.write_bytes(b"%PDF placeholder")

    calls = []

    def fake_leer_pdf(path, *, permitir_ocr=True):
        calls.append((Path(path), permitir_ocr))
        return {
            "texto_completo": (
                "FACTURA A 00013-00189814 06/08/2026 Fecha: "
                "INICIO ACTIV.: 01/04/2006"
            )
        }

    monkeypatch.setattr(pdf_reader, "leer_pdf", fake_leer_pdf)

    results = audit_organized_invoice_dates(root, apply=False)

    assert calls == [(source, False)]
    assert len(results) == 1
    assert results[0].status == "would_move"
    assert results[0].destination == root / "DBA" / "2026" / "08" / (
        "06-08FCA00013-00189814_MADERO_ROOF_TOP_DISTRIBUIDORA_DE_BEBIDAS_SRL.pdf"
    )


def test_factura_digital_completa_no_dispara_ocr_forzado(monkeypatch, tmp_path):
    import invoices.processor as processor
    import supplier_detector

    path = tmp_path / "Fc 189814.pdf"
    path.write_bytes(b"%PDF placeholder")

    digital = """
    A
    06/08/2026 Fecha:
    Nro: 00013-00189814
    Distribuidora de Bebidas SRL
    CUIT: 30-70942442-0
    IB: 901-673397-5
    INICIO ACTIV.:
    01/04/2006
    Cliente: MADERO ROOFTOP SA
    CUIT 30-71834746-3
    IVA Responsable Inscripto
    FACTURA
    Subtotal : $202,316.28
    IVA 21.00 $42,486.42
    Total : $256,941.68
    CAE: 86327172503529
    16/08/2026 Fecha Vencimiento CAE:
    """

    def fail_if_ocr(_path):
        raise AssertionError("Una factura digital completa no debe disparar OCR forzado")

    monkeypatch.setattr(processor.pdf_reader, "extraer_texto_ocr_forzado", fail_if_ocr)
    monkeypatch.setattr(
        processor,
        "mover_a_destino_final",
        lambda _origen, carpeta, nombre: Path(carpeta) / nombre,
    )
    monkeypatch.setattr(processor, "registrar_proveedor_ocasional", lambda **_kwargs: None)

    proveedor = supplier_detector.detectar_proveedor(
        digital + "\nNOMBRE ORIGINAL DEL ARCHIVO: Fc 189814.pdf"
    )
    result = processor.procesar_factura(path, digital, proveedor, tmp_path / "Facturas")

    assert result.organizada is True
    assert result.datos_factura.fecha_emision == "06/08/2026"
