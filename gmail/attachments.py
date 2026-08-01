"""Detección de archivos adjuntos dentro de un correo.

Detectar un adjunto no significa descargarlo. Este módulo identifica las partes
MIME relevantes y conserva el objeto ``parte`` para que ``file_manager`` pueda
obtener posteriormente sus bytes y guardarlos.
"""

from email.message import EmailMessage, Message
from typing import TypedDict


class Adjunto(TypedDict):
    """Estructura utilizada para describir un archivo adjunto."""

    nombre: str
    tipo_contenido: str
    parte: Message


def obtener_adjuntos(mensaje: EmailMessage) -> list[Adjunto]:
    """Recorrer el mensaje y devolver todos sus archivos adjuntos.

    Algunos emisores no marcan correctamente la disposición MIME como
    ``attachment``. Por eso también consideramos adjunta cualquier parte que
    tenga un nombre de archivo.
    """

    adjuntos: list[Adjunto] = []

    for parte in mensaje.walk():
        if parte.is_multipart():
            continue

        nombre_archivo = parte.get_filename()
        disposicion = parte.get_content_disposition()

        es_adjunto = (
            disposicion == "attachment"
            or nombre_archivo is not None
        )

        if not es_adjunto:
            continue

        adjuntos.append(
            {
                "nombre": nombre_archivo or "archivo_sin_nombre",
                "tipo_contenido": parte.get_content_type(),
                "parte": parte,
            }
        )

    return adjuntos
