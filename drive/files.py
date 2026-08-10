"""Consultas de archivos dentro de carpetas de Google Drive."""

from __future__ import annotations

from dataclasses import dataclass


PDF_MIME_TYPE = "application/pdf"


@dataclass(frozen=True)
class DriveFile:
    """Metadatos mínimos de un archivo remoto que el flujo necesita."""

    file_id: str
    name: str
    mime_type: str
    modified_time: str | None = None

    @property
    def is_pdf(self) -> bool:
        return self.mime_type == PDF_MIME_TYPE


def list_folder_files(service, folder_id: str) -> list[DriveFile]:
    """Listar todos los archivos directos de una carpeta, con paginación.

    Google Drive puede devolver resultados en varias páginas. El prototipo
    inicial funcionaba con 39 archivos, pero el módulo definitivo recorre todas
    las páginas para no perder documentos cuando la carpeta crezca.
    """

    if not folder_id.strip():
        raise ValueError("folder_id no puede estar vacío.")

    files: list[DriveFile] = []
    page_token: str | None = None

    while True:
        response = (
            service.files()
            .list(
                q=f"'{folder_id}' in parents and trashed = false",
                fields=(
                    "nextPageToken,"
                    "files(id,name,mimeType,modifiedTime)"
                ),
                orderBy="modifiedTime desc",
                pageSize=1000,
                pageToken=page_token,
            )
            .execute()
        )

        for item in response.get("files", []):
            files.append(
                DriveFile(
                    file_id=item["id"],
                    name=item["name"],
                    mime_type=item["mimeType"],
                    modified_time=item.get("modifiedTime"),
                )
            )

        page_token = response.get("nextPageToken")
        if not page_token:
            break

    return files
