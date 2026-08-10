import json
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload


# ============================================================
# CONFIGURACIÓN
# ============================================================

# Permiso de solo lectura sobre Google Drive.
SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly"
]

# Carpeta de Google Drive donde el proveedor sube las facturas.
PROVIDER_FOLDER_ID = "13rjMerJcrwuSoGg9LTxsQZAV9k0XnO-z"

# Archivos privados de autenticación OAuth.
CREDENTIALS_FILE = Path("credentials.json")
TOKEN_FILE = Path("token.json")

# Carpeta local que nuestro pipeline ya utiliza como
# bandeja de entrada para documentos pendientes.
PENDING_DIR = (
    Path.home()
    / "Documents"
    / "Facturas"
    / "_Pendientes"
)

# Carpeta donde guardamos datos internos del módulo.
DATA_DIR = Path("data")

# Registro de IDs de Google Drive ya descargados.
DOWNLOADED_IDS_FILE = (
    DATA_DIR
    / "drive_downloaded.json"
)


# ============================================================
# AUTENTICACIÓN
# ============================================================

def get_credentials():
    """
    Devuelve credenciales válidas para Google Drive.

    Flujo:
    1. Intenta reutilizar token.json si existe.
    2. Si el token expiró pero puede renovarse,
       lo renueva automáticamente.
    3. Si no existe un token válido, abre el navegador
       para solicitar autorización OAuth.
    4. Guarda el token actualizado para futuras ejecuciones.
    """

    credentials = None

    if TOKEN_FILE.exists():
        credentials = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES,
        )

    if (
        credentials
        and credentials.expired
        and credentials.refresh_token
    ):
        credentials.refresh(Request())

    if not credentials or not credentials.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE,
            SCOPES,
        )

        credentials = flow.run_local_server(
            port=0
        )

    TOKEN_FILE.write_text(
        credentials.to_json(),
        encoding="utf-8",
    )

    return credentials


# ============================================================
# CARPETAS LOCALES
# ============================================================

def ensure_pending_directory():
    """
    Garantiza que exista la carpeta local _Pendientes.

    Si faltara Facturas o _Pendientes,
    se crean automáticamente.

    Si ya existen, no genera ningún error.
    """

    PENDING_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    return PENDING_DIR


def ensure_data_directory():
    """
    Garantiza que exista la carpeta data/.
    """

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    return DATA_DIR


# ============================================================
# REGISTRO DE ARCHIVOS DESCARGADOS
# ============================================================

def load_downloaded_ids():
    """
    Lee drive_downloaded.json y devuelve un set
    con los fileId descargados anteriormente.

    Si el archivo todavía no existe,
    devuelve un conjunto vacío.
    """

    ensure_data_directory()

    if not DOWNLOADED_IDS_FILE.exists():
        return set()

    try:
        content = DOWNLOADED_IDS_FILE.read_text(
            encoding="utf-8"
        )

        data = json.loads(content)

        return set(
            data.get(
                "downloaded_file_ids",
                [],
            )
        )

    except (json.JSONDecodeError, OSError) as error:
        print()
        print(
            "ADVERTENCIA: no se pudo leer "
            "drive_downloaded.json."
        )
        print(
            f"Detalle: {error}"
        )
        print(
            "Para evitar perder documentos, "
            "se continuará con un registro vacío."
        )

        return set()


def save_downloaded_ids(downloaded_ids):
    """
    Guarda los IDs ya descargados en formato JSON.

    Guardamos después de cada descarga exitosa para que,
    si el programa se interrumpe posteriormente,
    los archivos anteriores sigan registrados.
    """

    ensure_data_directory()

    data = {
        "downloaded_file_ids": sorted(
            downloaded_ids
        )
    }

    json_content = json.dumps(
        data,
        indent=4,
        ensure_ascii=False,
    )

    DOWNLOADED_IDS_FILE.write_text(
        json_content,
        encoding="utf-8",
    )


# ============================================================
# GOOGLE DRIVE
# ============================================================

def build_drive_service():
    """
    Crea y devuelve el cliente de Google Drive API.
    """

    credentials = get_credentials()

    return build(
        "drive",
        "v3",
        credentials=credentials,
    )


def get_provider_files(service):
    """
    Obtiene los archivos existentes directamente dentro
    de la carpeta configurada para el proveedor.

    - Ignora archivos enviados a la papelera.
    - Los ordena desde el más recientemente modificado.
    """

    results = (
        service.files()
        .list(
            q=(
                f"'{PROVIDER_FOLDER_ID}' in parents "
                "and trashed = false"
            ),
            fields=(
                "files("
                "id,"
                "name,"
                "mimeType,"
                "modifiedTime"
                ")"
            ),
            orderBy="modifiedTime desc",
        )
        .execute()
    )

    return results.get(
        "files",
        [],
    )


# ============================================================
# DESCARGA DEFENSIVA
# ============================================================

def download_file(service, drive_file):
    """
    Descarga un archivo de Google Drive a _Pendientes.

    La descarga se realiza primero con extensión .part.

    Ejemplo:

        factura.pdf.part

    Solamente cuando Google confirma que terminó
    correctamente se renombra a:

        factura.pdf

    Esto evita que el pipeline procese PDFs incompletos.
    """

    pending_dir = ensure_pending_directory()

    filename = drive_file["name"]

    destination = (
        pending_dir
        / filename
    )

    temp_destination = (
        pending_dir
        / f"{filename}.part"
    )

    print(
        f"Descargando: {filename}"
    )

    print(
        f"Destino temporal: "
        f"{temp_destination}"
    )

    request = service.files().get_media(
        fileId=drive_file["id"]
    )

    try:
        with temp_destination.open(
            "wb"
        ) as output_file:

            downloader = MediaIoBaseDownload(
                output_file,
                request,
            )

            done = False

            while not done:
                status, done = (
                    downloader.next_chunk()
                )

                if status is not None:
                    progress = int(
                        status.progress()
                        * 100
                    )

                    print(
                        f"Progreso: {progress}%"
                    )

        # La descarga terminó correctamente.
        # Recién ahora hacemos visible el PDF definitivo.
        temp_destination.replace(
            destination
        )

        print(
            f"Descarga completada: "
            f"{destination}"
        )

        return destination

    except Exception:
        # Nunca dejamos un archivo parcial abandonado.
        if temp_destination.exists():
            temp_destination.unlink()

        raise


# ============================================================
# PROCESAMIENTO DE LA CARPETA DE DRIVE
# ============================================================

def process_provider_folder(service):
    """
    Recorre la carpeta del proveedor y descarga
    únicamente los PDFs nuevos.

    Un archivo se considera ya descargado utilizando
    su fileId único de Google Drive, no su nombre.
    """

    files = get_provider_files(
        service
    )

    downloaded_ids = load_downloaded_ids()

    downloaded_count = 0
    already_downloaded_count = 0
    ignored_count = 0
    error_count = 0

    print()
    print(
        "=========================================="
    )
    print(
        "CARPETA DE FACTURAS DEL PROVEEDOR"
    )
    print(
        "=========================================="
    )
    print(
        f"Archivos encontrados: {len(files)}"
    )

    if not files:
        print(
            "No hay archivos disponibles."
        )

        return {
            "downloaded": 0,
            "already_downloaded": 0,
            "ignored": 0,
            "errors": 0,
        }

    for drive_file in files:

        print()
        print(
            "------------------------------------------"
        )

        print(
            f"Archivo: {drive_file['name']}"
        )

        # ----------------------------------------------------
        # CONTROL 1: TIPO DE ARCHIVO
        # ----------------------------------------------------

        if (
            drive_file["mimeType"]
            != "application/pdf"
        ):
            print(
                "No es un archivo PDF. Se omite."
            )

            ignored_count += 1
            continue

        # ----------------------------------------------------
        # CONTROL 2: ID YA DESCARGADO
        # ----------------------------------------------------

        if (
            drive_file["id"]
            in downloaded_ids
        ):
            print(
                "Ya fue descargado anteriormente. "
                "Se omite."
            )

            already_downloaded_count += 1
            continue

        # ----------------------------------------------------
        # DESCARGA
        # ----------------------------------------------------

        try:
            download_file(
                service,
                drive_file,
            )

        except Exception as error:
            print(
                "ERROR: no se pudo descargar "
                "este archivo."
            )

            print(
                f"Detalle: {error}"
            )

            error_count += 1

            # Importante:
            # este ID no se registra.
            #
            # La próxima ejecución volverá a intentar
            # descargarlo.
            continue

        # ----------------------------------------------------
        # REGISTRO
        # ----------------------------------------------------

        # Llegamos acá solamente si la descarga
        # terminó correctamente.
        downloaded_ids.add(
            drive_file["id"]
        )

        try:
            save_downloaded_ids(
                downloaded_ids
            )

        except OSError as error:
            print(
                "ERROR: el archivo se descargó, "
                "pero no fue posible guardar su ID."
            )

            print(
                f"Detalle: {error}"
            )

            print(
                "ADVERTENCIA: en una próxima ejecución "
                "Drive podría intentar descargarlo nuevamente."
            )

            error_count += 1
            continue

        downloaded_count += 1

        print(
            "Archivo descargado y registrado "
            "correctamente."
        )

    return {
        "downloaded": downloaded_count,
        "already_downloaded": (
            already_downloaded_count
        ),
        "ignored": ignored_count,
        "errors": error_count,
    }


# ============================================================
# RESUMEN
# ============================================================

def print_summary(summary):
    """
    Muestra un resumen legible de la ejecución.
    """

    print()
    print(
        "=========================================="
    )
    print(
        "RESUMEN GOOGLE DRIVE"
    )
    print(
        "=========================================="
    )

    print(
        "PDF nuevos descargados: "
        f"{summary['downloaded']}"
    )

    print(
        "Ya descargados anteriormente: "
        f"{summary['already_downloaded']}"
    )

    print(
        "Archivos no PDF ignorados: "
        f"{summary['ignored']}"
    )

    print(
        "Errores: "
        f"{summary['errors']}"
    )

    print(
        "=========================================="
    )


# ============================================================
# PROGRAMA PRINCIPAL DE PRUEBA
# ============================================================

def main():
    """
    Prueba completa del flujo de descarga desde Drive.

    Todavía NO ejecuta el procesamiento de facturas.

    Únicamente:
    - conecta con Drive;
    - revisa la carpeta del proveedor;
    - descarga PDFs nuevos;
    - evita duplicados;
    - deja los documentos completos en _Pendientes.
    """

    try:
        service = build_drive_service()

    except Exception as error:
        print()
        print(
            "ERROR: no fue posible conectarse "
            "con Google Drive."
        )

        print(
            f"Detalle: {error}"
        )

        return

    summary = process_provider_folder(
        service
    )

    print_summary(
        summary
    )


# ============================================================
# PUNTO DE ENTRADA
# ============================================================

if __name__ == "__main__":
    main()