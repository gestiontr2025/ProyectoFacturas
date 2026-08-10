"""Descarga defensiva de archivos desde Google Drive."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from googleapiclient.http import MediaIoBaseDownload

from drive.files import DriveFile
from storage import sha256_file


INVALID_WINDOWS_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*]')


@dataclass(frozen=True)
class DriveDownloadResult:
    """Resultado de una descarga terminada de forma segura."""

    status: str
    path: Path
    detail: str = ""


def ensure_pending_directory(path: Path | str) -> Path:
    """Garantizar que exista la bandeja local ``_Pendientes``."""

    pending_dir = Path(path)
    pending_dir.mkdir(parents=True, exist_ok=True)
    return pending_dir


def _sanitize_filename(name: str, file_id: str) -> str:
    """Convertir un nombre de Drive en un nombre seguro para Windows.

    Se conserva la mayor cantidad de información posible porque el nombre del
    PDF puede aportar evidencia al parser. Solo se reemplazan caracteres que
    Windows no permite y se corrigen terminaciones problemáticas.
    """

    safe_name = INVALID_WINDOWS_FILENAME_CHARS.sub("_", name).strip().rstrip(". ")
    if safe_name:
        return safe_name
    return f"drive_{file_id}.pdf"


def _available_destination(destination: Path) -> Path:
    """Elegir un nombre libre sin sobrescribir un archivo diferente."""

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


def download_drive_file(
    service,
    drive_file: DriveFile,
    pending_dir: Path | str,
) -> DriveDownloadResult:
    """Descargar un archivo con protección contra cortes y colisiones.

    La descarga ocurre en ``_Pendientes/.drive_downloads`` usando extensión
    ``.part``. El PDF solo aparece en la raíz de ``_Pendientes`` después de que
    Google terminó de entregar todo el contenido.

    Si ya existe un archivo con el mismo nombre:

    - si el contenido es idéntico, se reutiliza la copia local;
    - si es diferente, ambos se conservan agregando ``_2``, ``_3``, etc.
    """

    pending = ensure_pending_directory(pending_dir)
    temp_dir = pending / ".drive_downloads"
    temp_dir.mkdir(parents=True, exist_ok=True)

    filename = _sanitize_filename(drive_file.name, drive_file.file_id)
    desired_destination = pending / filename
    temp_path = temp_dir / f"{drive_file.file_id}.part"

    # Una ejecución interrumpida puede haber dejado un .part antiguo. Nunca se
    # intenta reanudar a ciegas: se elimina y se empieza una descarga limpia.
    if temp_path.exists():
        temp_path.unlink()

    request = service.files().get_media(fileId=drive_file.file_id)

    try:
        with temp_path.open("wb") as output_file:
            downloader = MediaIoBaseDownload(output_file, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()

        if desired_destination.exists():
            if sha256_file(temp_path) == sha256_file(desired_destination):
                temp_path.unlink()
                return DriveDownloadResult(
                    status="local_duplicate",
                    path=desired_destination,
                    detail=(
                        "Ya existía una copia local idéntica; no se creó "
                        "un duplicado adicional."
                    ),
                )

            final_destination = _available_destination(desired_destination)
            temp_path.replace(final_destination)
            return DriveDownloadResult(
                status="downloaded_with_suffix",
                path=final_destination,
                detail=(
                    "Existía otro archivo con el mismo nombre pero contenido "
                    "diferente; se conservaron ambos."
                ),
            )

        temp_path.replace(desired_destination)
        return DriveDownloadResult(
            status="downloaded",
            path=desired_destination,
        )

    except Exception:
        if temp_path.exists():
            temp_path.unlink()
        raise
