"""Herramientas para comunicarse con Gmail mediante IMAP.

La carpeta ``gmail`` reúne funciones que antes estaban mezcladas dentro de
``gmail_client.py``. Cada módulo representa una responsabilidad distinta:

- ``connection``: abrir y cerrar la conexión.
- ``mailboxes``: localizar y seleccionar carpetas de Gmail.
- ``messages``: buscar, leer e interpretar correos.
- ``attachments``: detectar archivos adjuntos.

El resto del proyecto puede seguir importando ``gmail_client`` durante la
transición. Ese archivo funciona como una fachada de compatibilidad.
"""

from gmail.attachments import obtener_adjuntos
from gmail.connection import conectar
from gmail.mailboxes import encontrar_carpeta_todos
from gmail.messages import (
    buscar_todos_los_correos,
    leer_correo,
    obtener_identidad_correo,
    obtener_datos_correo,
)

__all__ = [
    "conectar",
    "encontrar_carpeta_todos",
    "buscar_todos_los_correos",
    "leer_correo",
    "obtener_identidad_correo",
    "obtener_datos_correo",
    "obtener_adjuntos",
]
