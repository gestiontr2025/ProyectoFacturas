"""Detección de duplicados y movimientos defensivos de archivos.

Dos documentos solo se consideran iguales cuando su contenido binario produce
la misma huella SHA-256. El nombre no alcanza: distintos comprobantes pueden
usar nombres genéricos como ``factura.pdf``.
"""

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import shutil


@dataclass(frozen=True)
class FileMoveResult:
    """Describir qué ocurrió al archivar un archivo.

    ``status`` puede ser:

    - ``moved``: el archivo fue trasladado normalmente.
    - ``duplicate_removed``: ya existía una copia idéntica y se eliminó
      únicamente la copia temporal.
    - ``moved_with_suffix``: existía otro archivo con el mismo nombre pero con
      contenido diferente; ambos se conservaron.
    """

    status: str
    destination: Path
    detail: str = ""


def sha256_bytes(content: bytes) -> str:
    """Calcular la huella SHA-256 de contenido que todavía está en memoria."""

    return sha256(content).hexdigest()


def sha256_file(path: Path | str) -> str:
    """Calcular SHA-256 leyendo el archivo por bloques.

    Leer por bloques evita cargar archivos grandes completamente en memoria.
    """

    digest = sha256()
    with Path(path).open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def find_identical_file(
    root: Path | str,
    *,
    content: bytes | None = None,
    source: Path | str | None = None,
    excluded_roots: tuple[Path | str, ...] = (),
) -> Path | None:
    """Buscar una copia idéntica dentro de un árbol de carpetas.

    Debe proporcionarse ``content`` o ``source``. Las carpetas excluidas son
    útiles para no comparar un archivo pendiente consigo mismo.
    """

    if content is None and source is None:
        raise ValueError("Debe proporcionarse content o source.")

    root_path = Path(root)
    source_path = Path(source).resolve() if source is not None else None
    expected_hash = sha256_bytes(content) if content is not None else sha256_file(source_path)
    excluded = tuple(Path(item).resolve() for item in excluded_roots)

    if not root_path.exists():
        return None

    for candidate in root_path.rglob("*.pdf"):
        resolved = candidate.resolve()
        if source_path is not None and resolved == source_path:
            continue
        if any(excluded_root == resolved or excluded_root in resolved.parents for excluded_root in excluded):
            continue
        try:
            if sha256_file(candidate) == expected_hash:
                return candidate
        except OSError:
            # Un archivo bloqueado o inaccesible no debe detener toda la
            # ejecución. Simplemente no puede utilizarse como prueba.
            continue
    return None


def _available_destination(destination: Path) -> Path:
    """Crear un nombre alternativo sin sobrescribir contenido diferente."""

    if not destination.exists():
        return destination

    counter = 2
    while True:
        candidate = destination.with_name(
            f"{destination.stem}_{counter}{destination.suffix}"
        )
        if not candidate.exists():
            return candidate
        counter += 1


def safe_archive_file(source: Path | str, destination_dir: Path | str) -> FileMoveResult:
    """Mover un archivo a una carpeta definitiva sin perder información.

    Si ya existe una copia idéntica, se elimina únicamente el archivo temporal.
    Si el nombre coincide pero el contenido es diferente, se conserva con un
    sufijo numérico.
    """

    source_path = Path(source)
    destination_folder = Path(destination_dir)
    destination_folder.mkdir(parents=True, exist_ok=True)
    desired = destination_folder / source_path.name

    identical = find_identical_file(destination_folder, source=source_path)
    if identical is not None:
        source_path.unlink()
        return FileMoveResult(
            status="duplicate_removed",
            destination=identical,
            detail="Ya existía una copia idéntica; se eliminó la copia redundante de _Pendientes.",
        )

    final_destination = _available_destination(desired)
    shutil.move(str(source_path), str(final_destination))
    if final_destination != desired:
        return FileMoveResult(
            status="moved_with_suffix",
            destination=final_destination,
            detail="Había otro archivo con el mismo nombre pero contenido diferente; se conservaron ambos.",
        )
    return FileMoveResult(status="moved", destination=final_destination)
