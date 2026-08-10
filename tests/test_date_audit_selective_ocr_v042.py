from datetime import date

import pdf_reader
from fiscal.issue_date import analizar_fecha_emision_para_auditoria
from storage.invoice_date_audit import audit_organized_invoice_dates


def test_fecha_generica_no_basta_para_mover_archivo():
    texto = """
    FACTURA C
    Fecha: 12/03/2026
    Vencimiento: 22/03/2026
    """
    analisis = analizar_fecha_emision_para_auditoria(
        texto,
        fecha_actual="02/03/2026",
        hoy=date(2026, 8, 9),
    )
    assert analisis.issue_date is None
    assert analisis.confidence in {"ambiguous", "none"}


def test_dba_fecha_antes_de_fecha_con_cabecera_fiscal_si_puede_corregir():
    texto = """
    A
    06/08/2026 Fecha:
    Nro: 00013-00189814
    FACTURA
    DISTRIBUIDORA DE BEBIDAS SRL
    INICIO ACTIV.: 01/04/2006
    CAE: 86327172503529
    16/08/2026 Fecha Vencimiento CAE:
    """
    analisis = analizar_fecha_emision_para_auditoria(
        texto,
        fecha_actual="01/04/2006",
        hoy=date(2026, 8, 9),
    )
    assert analisis.issue_date == "06/08/2026"
    assert analisis.confidence == "high"


def test_auditoria_no_usa_ocr_si_hay_texto_digital(monkeypatch, tmp_path):
    root = tmp_path / "Facturas"
    source = root / "PROVEEDOR" / "2026" / "03" / (
        "30-03FCC00001-00000127_MADERO_ROOF_TOP_PROVEEDOR.pdf"
    )
    source.parent.mkdir(parents=True)
    source.write_bytes(b"%PDF")

    monkeypatch.setattr(
        pdf_reader,
        "leer_pdf",
        lambda *_args, **_kwargs: {
            "texto_completo": "FACTURA C 00001-00000127 FECHA DE EMISION: 30/03/2026"
        },
    )

    def fail_ocr(*_args, **_kwargs):
        raise AssertionError("OCR no debe ejecutarse sobre un PDF digital")

    monkeypatch.setattr(pdf_reader, "extraer_texto_ocr_forzado", fail_ocr)
    assert audit_organized_invoice_dates(root, allow_ocr=True) == []


def test_ocr_selectivo_solo_rescata_pdf_sin_texto(monkeypatch, tmp_path):
    root = tmp_path / "Facturas"
    source = root / "PROVEEDOR" / "2028" / "08" / (
        "10-08FCA00001-00005606_MADERO_ROOF_TOP_PROVEEDOR.pdf"
    )
    source.parent.mkdir(parents=True)
    source.write_bytes(b"%PDF")

    monkeypatch.setattr(
        pdf_reader,
        "leer_pdf",
        lambda *_args, **_kwargs: {"texto_completo": ""},
    )
    monkeypatch.setattr(
        pdf_reader,
        "extraer_texto_ocr_forzado",
        lambda *_args, **_kwargs: {
            "texto_completo": "FACTURA A 00001-00005606 FECHA DE EMISION: 31/07/2026",
            "estado": "ok",
            "error": None,
        },
    )

    sin_ocr = audit_organized_invoice_dates(root, allow_ocr=False)
    assert sin_ocr[0].status == "skipped_no_digital_text"

    con_ocr = audit_organized_invoice_dates(root, allow_ocr=True)
    assert con_ocr[0].status == "would_move_ocr"
    assert con_ocr[0].destination.name.startswith("31-07FCA")


def test_cabecera_dba_real_cod_fecha_nro_tiene_confianza_maxima():
    texto = """
    A COD. 01 06/08/2026 FECHA: NRO: 00013-00189814
    DISTRIBUIDORA DE BEBIDAS SRL
    01/04/2006 VENTAS@DBA.COM.AR FACTURA
    CAE: 86327172503529 16/08/2026 FECHA VENCIMIENTO CAE:
    """
    analisis = analizar_fecha_emision_para_auditoria(
        texto,
        fecha_actual="01/04/2006",
        hoy=date(2026, 8, 9),
    )
    assert analisis.issue_date == "06/08/2026"
    assert analisis.confidence == "high"
    assert analisis.candidates[0].score == 100


def test_ocr_fecha_espaciada_puede_corregir_sin_tomar_vencimiento(monkeypatch, tmp_path):
    root = tmp_path / "Facturas"
    source = root / "PROVEEDOR" / "2028" / "08" / (
        "10-08FCA00001-00005606_MADERO_ROOF_TOP_PROVEEDOR.pdf"
    )
    source.parent.mkdir(parents=True)
    source.write_bytes(b"%PDF")
    monkeypatch.setattr(pdf_reader, "leer_pdf", lambda *_a, **_k: {"texto_completo": ""})
    monkeypatch.setattr(
        pdf_reader,
        "extraer_texto_ocr_forzado",
        lambda *_a, **_k: {
            "texto_completo": "FACTURA A 00001-00005606 FECHA: 31 07 2026 Venc.: 10/08/2026",
            "estado": "ok",
            "error": None,
        },
    )
    results = audit_organized_invoice_dates(root, allow_ocr=True)
    assert results[0].status == "would_move_ocr"
    assert results[0].destination.name.startswith("31-07FCA00001-00005606")
