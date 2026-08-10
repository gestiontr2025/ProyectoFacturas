"""Coordinación de descargas desde Google Drive hacia ``_Pendientes``.

Este módulo no interpreta facturas. Drive es solamente otra fuente de entrada,
igual que Gmail: descarga PDFs completos a ``_Pendientes`` y deja el análisis al
pipeline existente de ``--reprocess-pending``.
"""

from __future__ import annotations

from dataclasses import dataclass

import config
from drive.connection import build_drive_service
from drive.downloads import download_drive_file
from drive.files import list_folder_files
from infrastructure import get_logger
from state import DriveHistory, DriveIdentity


logger = get_logger(__name__)


@dataclass(frozen=True)
class DriveSource:
    """Carpeta remota configurada como fuente de documentos."""

    name: str
    folder_id: str


@dataclass
class DriveRunMetrics:
    """Contadores principales de una ejecución de Drive."""

    sources: int = 0
    found: int = 0
    pdf_candidates: int = 0
    skipped: int = 0
    downloaded: int = 0
    local_duplicates: int = 0
    ignored: int = 0
    errors: int = 0


def configured_drive_sources() -> list[DriveSource]:
    """Construir las fuentes activas a partir de ``.env``."""

    sources = []
    if config.DRIVE_PROVIDER_FOLDER_ID:
        sources.append(
            DriveSource(
                name="proveedor",
                folder_id=config.DRIVE_PROVIDER_FOLDER_ID,
            )
        )
    if config.DRIVE_SCAN_FOLDER_ID:
        sources.append(
            DriveSource(
                name="escaneos",
                folder_id=config.DRIVE_SCAN_FOLDER_ID,
            )
        )
    return sources


def run_drive_download() -> DriveRunMetrics:
    """Descargar todos los PDFs nuevos de las fuentes Drive configuradas."""

    config.validar_configuracion_drive()
    sources = configured_drive_sources()
    metrics = DriveRunMetrics(sources=len(sources))

    history = DriveHistory(config.STATE_DB_PATH)
    imported = history.import_legacy_json(config.LEGACY_DRIVE_HISTORY_PATH)
    if imported:
        logger.info(
            "Migrados %s IDs del antiguo drive_downloaded.json a SQLite.",
            imported,
        )

    service = build_drive_service(
        config.DRIVE_CREDENTIALS_PATH,
        config.DRIVE_TOKEN_PATH,
    )

    config.PENDING_FOLDER.mkdir(parents=True, exist_ok=True)

    for source in sources:
        logger.info(
            "Consultando Google Drive: source=%s folder_id=%s",
            source.name,
            source.folder_id,
        )
        files = list_folder_files(service, source.folder_id)
        metrics.found += len(files)

        print("\n" + "=" * 50)
        print(f"GOOGLE DRIVE — {source.name.upper()}")
        print("=" * 50)
        print(f"Archivos encontrados: {len(files)}")

        for drive_file in files:
            if not drive_file.is_pdf:
                metrics.ignored += 1
                logger.debug(
                    "Archivo Drive ignorado por MIME type: %s (%s)",
                    drive_file.name,
                    drive_file.mime_type,
                )
                continue

            metrics.pdf_candidates += 1
            identity = DriveIdentity(
                file_id=drive_file.file_id,
                source_name=source.name,
                folder_id=source.folder_id,
                file_name=drive_file.name,
                modified_time=drive_file.modified_time,
            )

            if history.is_completed(drive_file.file_id):
                metrics.skipped += 1
                continue

            try:
                result = download_drive_file(
                    service,
                    drive_file,
                    config.PENDING_FOLDER,
                )
                history_status = (
                    "local_duplicate"
                    if result.status == "local_duplicate"
                    else "downloaded"
                )
                history.mark_success(
                    identity,
                    local_path=result.path,
                    status=history_status,
                )

                if result.status == "local_duplicate":
                    metrics.local_duplicates += 1
                else:
                    metrics.downloaded += 1

                print(f"OK: {drive_file.name}")
                print(f"Ruta: {result.path}")
                if result.detail:
                    print(f"Detalle: {result.detail}")

            except Exception as error:
                history.mark_error(identity, error)
                metrics.errors += 1
                logger.exception(
                    "Error descargando archivo Drive %s (%s)",
                    drive_file.name,
                    drive_file.file_id,
                )
                print(f"ERROR: {drive_file.name}")
                print(f"Detalle: {error}")

    _show_drive_summary(metrics)
    return metrics


def _show_drive_summary(metrics: DriveRunMetrics) -> None:
    print("\n" + "=" * 50)
    print("RESUMEN GOOGLE DRIVE")
    print("=" * 50)
    print(f"Fuentes consultadas: {metrics.sources}")
    print(f"Archivos encontrados: {metrics.found}")
    print(f"PDF candidatos: {metrics.pdf_candidates}")
    print(f"PDF nuevos descargados: {metrics.downloaded}")
    print(f"Copias locales idénticas: {metrics.local_duplicates}")
    print(f"Ya descargados anteriormente: {metrics.skipped}")
    print(f"Archivos no PDF ignorados: {metrics.ignored}")
    print(f"Errores pendientes de reintento: {metrics.errors}")
    print(f"Destino: {config.PENDING_FOLDER}")
    print("=" * 50)
