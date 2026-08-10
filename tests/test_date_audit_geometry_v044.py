"""Regresiones para auditoría geométrica digital sin OCR."""

from pathlib import Path

import pytest

from fiscal.issue_date_geometry import extract_geometry_date_candidates
from storage.invoice_date_audit import audit_organized_invoice_dates

pymupdf = pytest.importorskip("pymupdf")


def _make_column_pdf(path: Path) -> None:
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((60, 80), "FACTURA C 00001-00000343", fontsize=10)
    page.insert_text((60, 130), "FECHA DE EMISION", fontsize=9)
    page.insert_text((300, 130), "FECHA DE VTO. PARA EL PAGO", fontsize=9)
    page.insert_text((60, 155), "02/03/2026", fontsize=10)
    page.insert_text((300, 155), "12/03/2026", fontsize=10)
    doc.save(path)
    doc.close()


def test_geometria_distingue_emision_de_vencimiento(tmp_path):
    pdf = tmp_path / "sample.pdf"
    _make_column_pdf(pdf)

    candidates = extract_geometry_date_candidates(pdf)

    assert candidates
    assert candidates[0].issue_date == "02/03/2026"
    assert candidates[0].score >= 96
    assert all(c.issue_date != "12/03/2026" for c in candidates if c.score >= 96)


def test_auditoria_corrige_nombre_danado_por_vencimiento_con_geometria(tmp_path):
    root = tmp_path / "Facturas"
    source = root / "PROVEEDOR" / "2026" / "03" / (
        "12-03FCC00001-00000343_MADERO_ROOF_TOP_PROVEEDOR.pdf"
    )
    source.parent.mkdir(parents=True)
    _make_column_pdf(source)

    results = audit_organized_invoice_dates(root, apply=False)

    moves = [r for r in results if r.status == "would_move"]
    assert len(moves) == 1
    assert moves[0].destination is not None
    assert moves[0].destination.name.startswith("02-03FCC00001-00000343")


def test_auditoria_no_usa_ocr_para_pdf_digital_con_geometria(monkeypatch, tmp_path):
    root = tmp_path / "Facturas"
    source = root / "PROVEEDOR" / "2026" / "03" / (
        "12-03FCC00001-00000343_MADERO_ROOF_TOP_PROVEEDOR.pdf"
    )
    source.parent.mkdir(parents=True)
    _make_column_pdf(source)

    import pdf_reader

    def forbidden(*_args, **_kwargs):
        raise AssertionError("La auditoría digital no debe activar OCR")

    monkeypatch.setattr(pdf_reader, "extraer_texto_ocr_forzado", forbidden)
    results = audit_organized_invoice_dates(root, allow_ocr=False)
    assert any(r.status == "would_move" for r in results)


def test_include_verified_permite_demostrar_que_se_auditaron_los_digitales(tmp_path):
    root = tmp_path / "Facturas"
    source = root / "PROVEEDOR" / "2026" / "03" / (
        "02-03FCC00001-00000343_MADERO_ROOF_TOP_PROVEEDOR.pdf"
    )
    source.parent.mkdir(parents=True)
    _make_column_pdf(source)

    results = audit_organized_invoice_dates(root, include_verified=True)
    assert len(results) == 1
    assert results[0].status == "verified_ok"


def _make_real_arca_flattened_pdf(path: Path) -> None:
    """Reproduce la geometría observada en comprobantes reales ARCA."""
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((60, 80), "FACTURA C 00001-00000394", fontsize=10)
    page.insert_text((341, 118), "Fecha de Emision:", fontsize=9)
    page.insert_text((428, 118), "05/08/2026", fontsize=10)
    page.insert_text((21, 187), "Período Facturado Desde:", fontsize=9)
    page.insert_text((159, 187), "03/08/2026", fontsize=10)
    page.insert_text((232, 187), "Hasta:", fontsize=9)
    page.insert_text((265, 187), "03/08/2026", fontsize=10)
    page.insert_text((363, 187), "Fecha de Vto. para el pago:", fontsize=9)
    page.insert_text((495, 187), "05/08/2026", fontsize=10)
    doc.save(path)
    doc.close()


def test_geometria_real_arca_no_confunde_periodo_con_emision(tmp_path):
    pdf = tmp_path / "real_arca.pdf"
    _make_real_arca_flattened_pdf(pdf)
    candidates = extract_geometry_date_candidates(pdf)
    strong = [c for c in candidates if c.score >= 96]
    assert [c.issue_date for c in strong] == ["05/08/2026"]


def test_auditoria_real_arca_prefiere_geometria_sobre_bloque_lineal(tmp_path):
    root = tmp_path / "Facturas"
    source = root / "PROVEEDOR" / "2026" / "08" / (
        "03-08FCC00001-00000394_MADERO_ROOF_TOP_PROVEEDOR.pdf"
    )
    source.parent.mkdir(parents=True)
    _make_real_arca_flattened_pdf(source)
    results = audit_organized_invoice_dates(root, apply=False)
    moves = [r for r in results if r.status == "would_move"]
    assert len(moves) == 1
    assert moves[0].destination.name.startswith("05-08FCC00001-00000394")
