from pathlib import Path

from models import Supplier
from suppliers.folder_migration import normalize_supplier_folders


def test_arta_always_uses_one_canonical_folder():
    supplier = Supplier(
        detected=True,
        identifier="arta_verduleros",
        legal_name="ARTA DE GONZALEZ S.R.L.",
        display_name="Arta Verduleros",
    )
    assert supplier.folder_name == "Arta Verduleros"


def test_el_criollo_always_uses_trade_folder():
    supplier = Supplier(
        detected=True,
        identifier="el_criollo",
        legal_name="DISTRIBUIDORA EL CRIOLLO SRL",
        display_name="El Criollo",
    )
    assert supplier.folder_name == "El Criollo"


def test_folder_migration_moves_legacy_files_without_overwriting(tmp_path: Path):
    source = tmp_path / "DISTRIBUIDORA_EL_CRIOLLO_SRL" / "2026" / "07"
    source.mkdir(parents=True)
    (source / "factura.pdf").write_bytes(b"legacy invoice")

    target = tmp_path / "EL_CRIOLLO" / "2026" / "07"
    target.mkdir(parents=True)
    (target / "factura.pdf").write_bytes(b"different invoice")

    results = normalize_supplier_folders(tmp_path)

    assert (target / "factura.pdf").read_bytes() == b"different invoice"
    assert (target / "factura_2.pdf").read_bytes() == b"legacy invoice"
    assert any(result.status == "movido_con_sufijo" for result in results)
    assert not (tmp_path / "DISTRIBUIDORA_EL_CRIOLLO_SRL").exists()


def test_folder_migration_removes_identical_duplicate(tmp_path: Path):
    source = tmp_path / "ARTA_DE_GONZALEZ_S_R_L" / "2026" / "07"
    target = tmp_path / "ARTA_VERDULEROS" / "2026" / "07"
    source.mkdir(parents=True)
    target.mkdir(parents=True)
    (source / "factura.pdf").write_bytes(b"same")
    (target / "factura.pdf").write_bytes(b"same")

    results = normalize_supplier_folders(tmp_path)

    assert (target / "factura.pdf").exists()
    assert not (tmp_path / "ARTA_DE_GONZALEZ_S_R_L").exists()
    assert any(result.status == "duplicado_eliminado" for result in results)
