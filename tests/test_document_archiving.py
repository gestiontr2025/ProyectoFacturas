"""Pruebas de archivo seguro para documentos administrativos."""

from pathlib import Path

from documents import TipoDocumento
from documents.organizer import archivar_otro_documento


def test_reprocessing_removes_identical_pending_copy(tmp_path: Path):
    pending = tmp_path / "_Pendientes"
    archived = tmp_path / "_OtrosDocumentos" / "Listas_de_precios"
    pending.mkdir()
    archived.mkdir(parents=True)

    pending_copy = pending / "lista.pdf"
    archived_copy = archived / "lista.pdf"
    pending_copy.write_bytes(b"same document")
    archived_copy.write_bytes(b"same document")

    result = archivar_otro_documento(
        pending_copy, tmp_path, TipoDocumento.LISTA_PRECIOS
    )

    assert result.status == "duplicate_removed"
    assert result.destination == archived_copy
    assert not pending_copy.exists()
    assert archived_copy.exists()


def test_same_name_different_content_keeps_both(tmp_path: Path):
    pending = tmp_path / "_Pendientes"
    archived = tmp_path / "_OtrosDocumentos" / "Ordenes_de_pago"
    pending.mkdir()
    archived.mkdir(parents=True)

    pending_copy = pending / "orden.pdf"
    existing = archived / "orden.pdf"
    pending_copy.write_bytes(b"new order")
    existing.write_bytes(b"old order")

    result = archivar_otro_documento(
        pending_copy, tmp_path, TipoDocumento.ORDEN_PAGO
    )

    assert result.status == "moved_with_suffix"
    assert result.destination.name == "orden_2.pdf"
    assert result.destination.read_bytes() == b"new order"
    assert existing.read_bytes() == b"old order"
