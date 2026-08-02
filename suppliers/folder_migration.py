"""Migración segura de carpetas duplicadas de proveedores.

La migración reúne carpetas históricas que representan al mismo proveedor.
No reemplaza archivos silenciosamente y solo elimina carpetas que quedaron
vacías después de mover su contenido.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import shutil

from suppliers.folder_names import get_known_folder_aliases


@dataclass(frozen=True)
class FolderMigrationResult:
    """Describe one action performed during folder normalization."""

    source: Path
    destination: Path
    status: str
    detail: str = ""


def _file_digest(path: Path) -> str:
    """Calculate a content hash without loading the whole file into memory."""
    digest = sha256()
    with path.open("rb") as file_handle:
        for block in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _same_file_content(first: Path, second: Path) -> bool:
    """Compare size first and hash only when necessary."""
    return first.stat().st_size == second.stat().st_size and _file_digest(first) == _file_digest(second)


def _non_colliding_path(desired: Path) -> Path:
    """Create a safe alternative name when different files share a name."""
    if not desired.exists():
        return desired

    counter = 2
    while True:
        candidate = desired.with_name(f"{desired.stem}_{counter}{desired.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def _remove_empty_tree(path: Path, stop_at: Path) -> None:
    """Remove empty directories from the bottom up, never above ``stop_at``."""
    current = path
    while current != stop_at and current.exists():
        try:
            current.rmdir()
        except OSError:
            break
        current = current.parent


def normalize_supplier_folders(root_folder: str | Path) -> list[FolderMigrationResult]:
    """Merge known legacy supplier folders into canonical folders.

    Safety rules:
        - Existing different files are never overwritten.
        - Identical duplicates are detected by SHA-256 before one copy is removed.
        - Unknown folders are not touched.
        - Only empty source directories are removed.
    """
    root = Path(root_folder)
    root.mkdir(parents=True, exist_ok=True)
    results: list[FolderMigrationResult] = []

    for legacy_name, canonical_name in get_known_folder_aliases().items():
        source_folder = root / legacy_name
        target_folder = root / canonical_name

        if legacy_name == canonical_name or not source_folder.exists():
            continue

        for source_file in sorted(path for path in source_folder.rglob("*") if path.is_file()):
            relative_path = source_file.relative_to(source_folder)
            desired_destination = target_folder / relative_path
            desired_destination.parent.mkdir(parents=True, exist_ok=True)

            if desired_destination.exists() and _same_file_content(source_file, desired_destination):
                source_file.unlink()
                results.append(FolderMigrationResult(
                    source=source_file,
                    destination=desired_destination,
                    status="duplicado_eliminado",
                    detail="El destino ya contenía un archivo idéntico.",
                ))
                continue

            final_destination = _non_colliding_path(desired_destination)
            shutil.move(str(source_file), str(final_destination))
            status = "movido" if final_destination == desired_destination else "movido_con_sufijo"
            detail = "" if status == "movido" else "Se agregó un sufijo para evitar sobrescribir otro archivo."
            results.append(FolderMigrationResult(
                source=source_file,
                destination=final_destination,
                status=status,
                detail=detail,
            ))

        # Remove nested empty folders and finally the legacy root if possible.
        for directory in sorted(
            (path for path in source_folder.rglob("*") if path.is_dir()),
            key=lambda item: len(item.parts),
            reverse=True,
        ):
            _remove_empty_tree(directory, root)
        _remove_empty_tree(source_folder, root)

    return results
