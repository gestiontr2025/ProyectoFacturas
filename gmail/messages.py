"""Búsqueda, lectura e interpretación básica de correos.

Este módulo trabaja con mensajes, pero no descarga sus adjuntos. Esa separación
ayuda a distinguir dos conceptos diferentes: leer un correo y guardar archivos
en el disco.
"""

import email
import imaplib
from email import policy
from email.message import EmailMessage

from gmail.mailboxes import encontrar_carpeta_todos


def buscar_todos_los_correos(
    conexion: imaplib.IMAP4_SSL,
) -> list[bytes]:
    """Buscar los identificadores IMAP de todos los mensajes.

    Los identificadores devueltos pertenecen a la carpeta seleccionada y a la
    sesión actual. No son el encabezado público ``Message-ID`` del correo.
    """

    carpeta_todos = encontrar_carpeta_todos(conexion)

    estado_seleccion, _ = conexion.select(
        carpeta_todos,
        readonly=True,
    )

    if estado_seleccion != "OK":
        raise RuntimeError(
            "No fue posible seleccionar la carpeta de todos los correos."
        )

    estado_busqueda, respuesta = conexion.search(None, "ALL")

    if estado_busqueda != "OK":
        raise RuntimeError(
            "Gmail no pudo completar la búsqueda de correos."
        )

    if not respuesta:
        raise RuntimeError(
            "Gmail devolvió una respuesta vacía durante la búsqueda."
        )

    identificadores = respuesta[0]

    if not isinstance(identificadores, bytes):
        raise RuntimeError(
            "La respuesta de Gmail no contiene identificadores válidos."
        )

    return identificadores.split()


def leer_correo(
    conexion: imaplib.IMAP4_SSL,
    id_correo: bytes,
) -> EmailMessage:
    """Descargar un correo completo en memoria y convertirlo en EmailMessage.

    La función no escribe nada en el disco. Obtener el mensaje en memoria nos
    permite revisar primero sus encabezados y adjuntos antes de decidir qué
    archivos guardar.
    """

    estado, respuesta = conexion.fetch(id_correo, "(RFC822)")

    if estado != "OK":
        raise RuntimeError(
            f"No fue posible obtener el correo con ID {id_correo!r}."
        )

    if not respuesta:
        raise RuntimeError(
            "Gmail devolvió una respuesta vacía al leer el correo."
        )

    primer_elemento = respuesta[0]

    if not isinstance(primer_elemento, tuple):
        raise RuntimeError(
            "La respuesta recibida no tiene la estructura esperada."
        )

    if len(primer_elemento) < 2:
        raise RuntimeError("La respuesta del correo está incompleta.")

    correo_bytes = primer_elemento[1]

    if not isinstance(correo_bytes, bytes):
        raise RuntimeError(
            "El contenido del correo no fue recibido en formato bytes."
        )

    mensaje = email.message_from_bytes(
        correo_bytes,
        policy=policy.default,
    )

    # Con policy.default Python devuelve normalmente EmailMessage. La
    # comprobación deja un error explícito si una implementación futura cambia.
    if not isinstance(mensaje, EmailMessage):
        raise RuntimeError(
            "Python no pudo convertir el correo en un EmailMessage."
        )

    return mensaje


def obtener_datos_correo(mensaje: EmailMessage) -> dict[str, str]:
    """Extraer los encabezados que necesita el flujo actual.

    Se mantienen las claves originales para no romper los módulos que todavía
    consumen este diccionario durante la refactorización.
    """

    return {
        "Subject": str(mensaje.get("Subject", "Sin asunto")),
        "From": str(
            mensaje.get("From", "Remitente no informado")
        ),
        "To": str(
            mensaje.get("To", "Destinatario no informado")
        ),
        "Date": str(mensaje.get("Date", "Fecha no informada")),
    }
