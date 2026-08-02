"""Pruebas de deduplicación segura para comprobantes fiscales."""

from pathlib import Path

from storage.invoice_duplicates import (
    cleanup_exact_invoice_duplicates,
    fiscal_key_from_filename,
    safe_move_invoice,
)


def test_extracts_fiscal_key_from_canonical_filename():
    name = "31-07FCA00006-00343487_MADERO_ROOF_TOP_HORECA_SRL.pdf"
    assert fiscal_key_from_filename(name) == "FCA:00006:00343487"


def test_safe_move_removes_identical_temporary_invoice(tmp_path: Path):
    pending = tmp_path / "_Pendientes"
    destination = tmp_path / "HORECA_SRL" / "2026" / "07"
    pending.mkdir()
    destination.mkdir(parents=True)

    source = pending / "original.pdf"
    existing = destination / "31-07FCA00006-00343487_EMPRESA_HORECA.pdf"
    source.write_bytes(b"same invoice")
    existing.write_bytes(b"same invoice")

    result = safe_move_invoice(
        source,
        destination,
        "31-07FCA00006-00343487_EMPRESA_HORECA.pdf",
    )

    assert result.status == "duplicate_removed"
    assert result.destination == existing
    assert not source.exists()


def test_same_fiscal_key_different_content_preserves_both(tmp_path: Path):
    pending = tmp_path / "_Pendientes"
    destination = tmp_path / "HORECA_SRL" / "2026" / "07"
    pending.mkdir()
    destination.mkdir(parents=True)

    source = pending / "new.pdf"
    existing = destination / "31-07FCA00006-00343487_EMPRESA_HORECA.pdf"
    source.write_bytes(b"new representation")
    existing.write_bytes(b"old representation")

    result = safe_move_invoice(
        source,
        destination,
        "31-07FCA00006-00343487_EMPRESA_HORECA.pdf",
    )

    assert result.status == "fiscal_conflict"
    assert result.destination.name.endswith("_2.pdf")
    assert existing.exists()
    assert result.destination.exists()


def test_cleanup_is_preview_by_default(tmp_path: Path):
    first = tmp_path / "A" / "2026" / "07" / "one.pdf"
    second = tmp_path / "B" / "2026" / "07" / "two.pdf"
    first.parent.mkdir(parents=True)
    second.parent.mkdir(parents=True)
    first.write_bytes(b"duplicate")
    second.write_bytes(b"duplicate")

    results = cleanup_exact_invoice_duplicates(tmp_path)

    assert len(results) == 1
    assert results[0].status == "would_remove"
    assert first.exists() and second.exists()


def test_cleanup_apply_deletes_only_exact_copy(tmp_path: Path):
    first = tmp_path / "A" / "2026" / "07" / "one.pdf"
    second = tmp_path / "B" / "2026" / "07" / "two.pdf"
    first.parent.mkdir(parents=True)
    second.parent.mkdir(parents=True)
    first.write_bytes(b"duplicate")
    second.write_bytes(b"duplicate")

    results = cleanup_exact_invoice_duplicates(tmp_path, apply=True)

    assert len(results) == 1
    assert results[0].status == "duplicate_removed"
    assert results[0].survivor.exists()
    assert not results[0].duplicate.exists()
