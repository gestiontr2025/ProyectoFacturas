"""Configuración general del Proyecto Facturas.

Este módulo centraliza los valores que pueden cambiar entre computadoras. La
lógica del programa no debería contener correos, contraseñas ni rutas locales:
esos valores pertenecen al archivo ``.env`` de cada instalación.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


# La ruta se calcula desde este archivo para encontrar .env aunque el programa
# se ejecute desde otra carpeta en la terminal.
PROJECT_ROOT = Path(__file__).resolve().parent
ENV_FILE = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=ENV_FILE)

PROJECT_NAME = "Proyecto Facturas"
PROJECT_AUTHOR = "Diego"

EMAIL = os.getenv("EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
EMAIL_PROCESSING_LIMIT = int(
    os.getenv("EMAIL_PROCESSING_LIMIT", "10")
)

# Path.home() adapta automáticamente la ruta al usuario de cada computadora.
# En Windows produce, por ejemplo, C:\Users\piola.
DEFAULT_SAVE_FOLDER = Path.home() / "Documents" / "Facturas"


def obtener_ruta_desde_entorno(
    nombre_variable: str,
    ruta_predeterminada: Path,
) -> Path:
    """Obtener una ruta desde .env o usar una alternativa automática.

    Una variable vacía se considera deliberadamente no configurada. Esto hace
    posible distribuir un ``.env.example`` genérico sin obligar a cada persona
    a conocer su nombre de usuario de Windows.
    """

    valor_configurado = os.getenv(nombre_variable, "").strip()

    if not valor_configurado:
        return ruta_predeterminada

    return Path(valor_configurado).expanduser().resolve()


SAVE_FOLDER = obtener_ruta_desde_entorno(
    "SAVE_FOLDER",
    DEFAULT_SAVE_FOLDER,
)


def validar_configuracion() -> None:
    """Detectar configuraciones inválidas antes de conectarse a Gmail."""

    variables_faltantes = []

    if not EMAIL:
        variables_faltantes.append("EMAIL")

    if not APP_PASSWORD:
        variables_faltantes.append("APP_PASSWORD")

    if variables_faltantes:
        nombres = ", ".join(variables_faltantes)
        raise ValueError(
            "Faltan variables obligatorias en el archivo .env: "
            f"{nombres}."
        )

    if EMAIL_PROCESSING_LIMIT <= 0:
        raise ValueError(
            "EMAIL_PROCESSING_LIMIT debe ser un número mayor que cero."
        )


validar_configuracion()
