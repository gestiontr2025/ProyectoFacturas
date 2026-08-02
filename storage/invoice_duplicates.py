"""Deduplicación segura de comprobantes fiscales organizados.

Este módulo aplica dos comprobaciones complementarias:

1. **Contenido idéntico**: dos archivos con el mismo SHA-256 son copias
   exactas. En ese caso puede eliminarse la copia temporal sin perder datos.
2. **Identidad fiscal**: el tipo, la letra, el punto de venta y el número
   identifican un comprobante. Si dos archivos comparten esa identidad pero
   tienen contenido distinto, se conservan ambos y se informa un conflicto.

La segunda regla es deliberadamente conservadora: una diferencia binaria puede
representar una versión corregida, una copia con firma, o un PDF regenerado.
El programa nunca decide cuál borrar sin una prueba de igualdad exacta.
"""

from dataclasses import dataclass
from pathlib import Path
import re
import shutil

from storage.duplicates import find_identical_file, sha256_file


_FISCAL_KEY_PATTERN = re.compile(
    r"^\d{2}-\d{2}(?P<code>(?:FC|NC|ND)[ABC])"
    r"(?P<point>\d{4,5})-(?P<number>\d{6,10})(?:_|\.pdf$)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class InvoiceMoveResult:
    """Resultado de mover una factura a su ubicación definitiva.

    Estados posibles:

    - ``moved``: se trasladó normalmente.
    - ``duplicate_removed``: ya existía una copia binariamente idéntica.
    - ``fiscal_conflict``: existe el mismo comprobante fiscal con contenido
      distinto; se conservaron ambas versiones con nombres diferentes.
    """

    status: str
    destination: Path
    detail: str = ""


@dataclass(frozen=True)
class DuplicateCleanupResult:
    """Acción propuesta o realizada por el limpiador de duplicados."""

    status: str
    duplicate: Path
    survivor: Path
    detail: str = ""


def fiscal_key_from_filename(filename: str) -> str | None:
    """Extraer una identidad fiscal desde el nombre normalizado del PDF.

    Ejemplo:
        ``31-07FCA00006-00343487_...pdf``
        se transforma en ``FCA:00006:00343487``.

    Los nombres que no siguen el formato final del proyecto devuelven ``None``.
    """

    match = _FISCAL_KEY_PATTERN.search(Path(filename).name)
    if match is None:
        return None
    return ":".join(
        (
            match.group("code").upper(),
            match.group("point").zfill(5),
            match.group("number").zfill(8),
        )
    )


def _available_destination(destination: Path) -> Path:
    """Elegir un nombre libre sin reemplazar un archivo existente."""

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


def _same_fiscal_key_files(folder: Path, fiscal_key: str) -> list[Path]:
    """Encontrar comprobantes de la carpeta con la misma identidad fiscal."""

    return [
        candidate
        for candidate in folder.glob("*.pdf")
        if fiscal_key_from_filename(candidate.name) == fiscal_key
    ]


def safe_move_invoice(
    source: Path | str,
    destination_dir: Path | str,
    final_name: str,
) -> InvoiceMoveResult:
    """Mover una factura sin crear una segunda copia idéntica.

    Primero se compara el contenido con todos los PDF de la carpeta final. Si
    ya existe una copia exacta, se elimina únicamente el archivo temporal.

    Si existe el mismo comprobante fiscal pero el hash difiere, ambos archivos
    se conservan. Esta es una señal que requiere revisión humana, no una razón
    suficiente para borrar información.
    """

    source_path = Path(source)
    folder = Path(destination_dir)
    folder.mkdir(parents=True, exist_ok=True)

    identical = find_identical_file(folder, source=source_path)
    if identical is not None:
        source_path.unlink()
        return InvoiceMoveResult(
            status="duplicate_removed",
            destination=identical,
            detail=(
                "Ya existía una copia idéntica en la carpeta del proveedor; "
                "se eliminó únicamente la copia temporal."
            ),
        )

    desired = folder / final_name
    fiscal_key = fiscal_key_from_filename(final_name)
    conflicts = _same_fiscal_key_files(folder, fiscal_key) if fiscal_key else []

    destination = _available_destination(desired)
    shutil.move(str(source_path), str(destination))

    if conflicts:
        return InvoiceMoveResult(
            status="fiscal_conflict",
            destination=destination,
            detail=(
                "Ya existía un archivo con la misma identidad fiscal pero "
                "contenido diferente; se conservaron ambas versiones."
            ),
        )

    return InvoiceMoveResult(status="moved", destination=destination)


def _invoice_files(root: Path) -> list[Path]:
    """Listar facturas organizadas, excluyendo carpetas de trabajo internas."""

    if not root.exists():
        return []

    result = []
    for candidate in root.rglob("*.pdf"):
        relative = candidate.relative_to(root)
        if relative.parts and relative.parts[0].startswith("_"):
            continue
        result.append(candidate)
    return sorted(result)


def find_exact_invoice_duplicates(root: Path | str) -> list[tuple[Path, Path]]:
    """Encontrar pares de copias exactas entre facturas ya organizadas.

    El primer archivo de cada grupo se conserva como superviviente. La elección
    es determinista: se ordenan las rutas alfabéticamente para que una vista
    previa y la ejecución real propongan siempre la misma acción.
    """

    groups: dict[str, list[Path]] = {}
    for path in _invoice_files(Path(root)):
        try:
            groups.setdefault(sha256_file(path), []).append(path)
        except OSError:
            continue

    duplicates: list[tuple[Path, Path]] = []
    for paths in groups.values():
        if len(paths) < 2:
            continue
        ordered = sorted(paths, key=lambda item: str(item).casefold())
        survivor = ordered[0]
        duplicates.extend((duplicate, survivor) for duplicate in ordered[1:])
    return duplicates


def cleanup_exact_invoice_duplicates(
    root: Path | str,
    *,
    apply: bool = False,
) -> list[DuplicateCleanupResult]:
    """Informar o eliminar duplicados exactos de facturas organizadas.

    Por defecto funciona como vista previa y no borra nada. Solo cuando
    ``apply=True`` elimina las copias cuyo SHA-256 coincide exactamente con el
    archivo superviviente.
    """

    results = []
    for duplicate, survivor in find_exact_invoice_duplicates(root):
        if apply:
            duplicate.unlink()
            status = "duplicate_removed"
            detail = "Copia idéntica eliminada después de verificar SHA-256."
        else:
            status = "would_remove"
            detail = "Vista previa: no se modificó ningún archivo."
        results.append(
            DuplicateCleanupResult(
                status=status,
                duplicate=duplicate,
                survivor=survivor,
                detail=detail,
            )
        )
    return results
