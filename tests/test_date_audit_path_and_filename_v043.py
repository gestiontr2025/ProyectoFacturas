"""Regresiones para reparación conjunta de carpeta y nombre en auditoría."""

from pathlib import Path

import pdf_reader
from storage.invoice_date_audit import audit_organized_invoice_dates


PDF_TEXT = (
    "FACTURA C 00001-00000343 "
    "FECHA DE EMISION: 02/03/2026 "
    "CAE: 12345678901234"
)


def _mock_text(monkeypatch):
    monkeypatch.setattr(
        pdf_reader,
        "leer_pdf",
        lambda *_args, **_kwargs: {"texto_completo": PDF_TEXT},
    )


def test_auditoria_renombra_si_carpeta_esta_bien_pero_fecha_del_nombre_no(monkeypatch, tmp_path):
    _mock_text(monkeypatch)
    root = tmp_path / "Facturas"
    source = root / "PROVEEDOR" / "2026" / "03" / (
        "12-03FCC00001-00000343_MADERO_ROOF_TOP_PROVEEDOR.pdf"
    )
    source.parent.mkdir(parents=True)
    source.write_bytes(b"%PDF")

    results = audit_organized_invoice_dates(root)

    assert len(results) == 1
    result = results[0]
    assert result.status == "would_move"
    assert result.destination.parent == source.parent
    assert result.destination.name == (
        "02-03FCC00001-00000343_MADERO_ROOF_TOP_PROVEEDOR.pdf"
    )


def test_auditoria_mueve_si_nombre_esta_bien_pero_carpeta_es_incorrecta(monkeypatch, tmp_path):
    _mock_text(monkeypatch)
    root = tmp_path / "Facturas"
    source = root / "PROVEEDOR" / "2026" / "04" / (
        "02-03FCC00001-00000343_MADERO_ROOF_TOP_PROVEEDOR.pdf"
    )
    source.parent.mkdir(parents=True)
    source.write_bytes(b"%PDF")

    results = audit_organized_invoice_dates(root)

    assert len(results) == 1
    result = results[0]
    assert result.status == "would_move"
    assert result.destination == root / "PROVEEDOR" / "2026" / "03" / source.name


def test_auditoria_corrige_carpeta_y_nombre_en_una_sola_operacion(monkeypatch, tmp_path):
    _mock_text(monkeypatch)
    root = tmp_path / "Facturas"
    source = root / "PROVEEDOR" / "2026" / "04" / (
        "12-04FCC00001-00000343_MADERO_ROOF_TOP_PROVEEDOR.pdf"
    )
    source.parent.mkdir(parents=True)
    source.write_bytes(b"%PDF")

    preview = audit_organized_invoice_dates(root, apply=False)
    assert preview[0].destination == (
        root
        / "PROVEEDOR"
        / "2026"
        / "03"
        / "02-03FCC00001-00000343_MADERO_ROOF_TOP_PROVEEDOR.pdf"
    )

    applied = audit_organized_invoice_dates(root, apply=True)
    assert applied[0].status == "date_repaired"
    assert applied[0].destination.exists()
    assert not source.exists()


def test_auditoria_no_hace_nada_si_carpeta_y_nombre_ya_son_canonicos(monkeypatch, tmp_path):
    _mock_text(monkeypatch)
    root = tmp_path / "Facturas"
    source = root / "PROVEEDOR" / "2026" / "03" / (
        "02-03FCC00001-00000343_MADERO_ROOF_TOP_PROVEEDOR.pdf"
    )
    source.parent.mkdir(parents=True)
    source.write_bytes(b"%PDF")

    assert audit_organized_invoice_dates(root) == []
