"""Autenticación OAuth y creación del cliente de Google Drive.

Las credenciales privadas permanecen fuera del código fuente. ``credentials.json``
identifica la aplicación OAuth y ``token.json`` conserva la autorización del
usuario para que no sea necesario abrir el navegador en cada ejecución.
"""

from __future__ import annotations

from pathlib import Path

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


DEFAULT_DRIVE_SCOPES = (
    "https://www.googleapis.com/auth/drive.readonly",
)


def get_drive_credentials(
    credentials_path: Path | str,
    token_path: Path | str,
    *,
    scopes: tuple[str, ...] = DEFAULT_DRIVE_SCOPES,
) -> Credentials:
    """Obtener credenciales OAuth válidas para Google Drive.

    El flujo es defensivo:

    - reutiliza ``token.json`` cuando es válido;
    - intenta renovarlo automáticamente cuando expiró;
    - si fue revocado o quedó inválido, vuelve a pedir autorización;
    - guarda el token actualizado solo después de obtener credenciales válidas.
    """

    credentials_file = Path(credentials_path)
    token_file = Path(token_path)
    token_file.parent.mkdir(parents=True, exist_ok=True)

    if not credentials_file.exists():
        raise FileNotFoundError(
            "No se encontró el archivo de credenciales de Google Drive: "
            f"{credentials_file}"
        )

    credentials: Credentials | None = None

    if token_file.exists():
        try:
            credentials = Credentials.from_authorized_user_file(
                token_file,
                list(scopes),
            )
        except (OSError, ValueError):
            # Un token corrupto o incompatible no debe bloquear la aplicación.
            # Se solicitará una nueva autorización más abajo.
            credentials = None

    if credentials and credentials.expired and credentials.refresh_token:
        try:
            credentials.refresh(Request())
        except RefreshError:
            # El usuario pudo revocar el acceso desde su cuenta de Google.
            credentials = None

    if not credentials or not credentials.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_file,
            list(scopes),
        )
        credentials = flow.run_local_server(port=0)

    token_file.write_text(
        credentials.to_json(),
        encoding="utf-8",
    )
    return credentials


def build_drive_service(
    credentials_path: Path | str,
    token_path: Path | str,
    *,
    scopes: tuple[str, ...] = DEFAULT_DRIVE_SCOPES,
):
    """Crear el cliente ``drive v3`` listo para consultar archivos."""

    credentials = get_drive_credentials(
        credentials_path,
        token_path,
        scopes=scopes,
    )
    return build(
        "drive",
        "v3",
        credentials=credentials,
        cache_discovery=False,
    )
