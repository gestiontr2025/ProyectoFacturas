"""Búsqueda, identidad y lectura de correos de Gmail mediante IMAP.

La identidad se consulta por separado del cuerpo completo. De este modo, una
ejecución diaria puede comprobar primero si un correo ya fue procesado y evitar
descargar nuevamente todo su contenido y sus adjuntos.
"""

from __future__ import annotations

import email
import imaplib
import re
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser

from gmail.mailboxes import encontrar_carpeta_todos
from state import EmailIdentity


def buscar_todos_los_correos(
    conexion: imaplib.IMAP4_SSL,
) -> list[bytes]:
    """Buscar los números de secuencia de todos los mensajes en ``All Mail``.

    Los números de secuencia solo se usan para operar durante la sesión actual.
    El historial persistente no depende de ellos: utiliza ``X-GM-MSGID``.
    """

    carpeta_todos = encontrar_carpeta_todos(conexion)
    estado_seleccion, _ = conexion.select(carpeta_todos, readonly=True)
    if estado_seleccion != "OK":
        raise RuntimeError(
            "No fue posible seleccionar la carpeta de todos los correos."
        )

    estado_busqueda, respuesta = conexion.search(None, "ALL")
    if estado_busqueda != "OK":
        raise RuntimeError("Gmail no pudo completar la búsqueda de correos.")
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


def obtener_identidad_correo(
    conexion: imaplib.IMAP4_SSL,
    id_correo: bytes,
) -> EmailIdentity:
    """Obtener identidad estable y encabezados sin descargar el correo completo.

    Gmail expone ``X-GM-MSGID`` como identificador global. Cuando no estuviera
    disponible, se usa el encabezado estándar ``Message-ID``. El número de
    secuencia IMAP queda como último respaldo para no bloquear la ejecución,
    aunque no es estable entre sesiones.
    """

    query = "(X-GM-MSGID BODY.PEEK[HEADER.FIELDS (MESSAGE-ID SUBJECT DATE)])"
    estado, respuesta = conexion.fetch(id_correo, query)
    if estado != "OK" or not respuesta:
        raise RuntimeError(
            f"No fue posible obtener la identidad del correo {id_correo!r}."
        )

    metadata = b""
    header_bytes = b""
    for element in respuesta:
        if isinstance(element, tuple):
            if element and isinstance(element[0], bytes):
                metadata += element[0]
            if len(element) > 1 and isinstance(element[1], bytes):
                header_bytes += element[1]
        elif isinstance(element, bytes):
            metadata += element

    gm_match = re.search(rb"X-GM-MSGID\s+(\d+)", metadata)
    gmail_message_id = gm_match.group(1).decode("ascii") if gm_match else None

    headers = BytesParser(policy=policy.default).parsebytes(header_bytes)
    rfc_message_id = str(headers.get("Message-ID", "")).strip() or None
    subject = str(headers.get("Subject", "Sin asunto"))
    message_date = str(headers.get("Date", "Fecha no informada"))

    if gmail_message_id:
        source_key = f"gmail:{gmail_message_id}"
    elif rfc_message_id:
        source_key = f"message-id:{rfc_message_id}"
    else:
        source_key = f"imap-sequence:{id_correo.decode(errors='replace')}"

    return EmailIdentity(
        source_key=source_key,
        gmail_message_id=gmail_message_id,
        rfc_message_id=rfc_message_id,
        subject=subject,
        message_date=message_date,
    )


def leer_correo(
    conexion: imaplib.IMAP4_SSL,
    id_correo: bytes,
) -> EmailMessage:
    """Descargar un correo completo en memoria y convertirlo en EmailMessage."""

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
    if not isinstance(primer_elemento, tuple) or len(primer_elemento) < 2:
        raise RuntimeError("La respuesta del correo está incompleta.")

    correo_bytes = primer_elemento[1]
    if not isinstance(correo_bytes, bytes):
        raise RuntimeError(
            "El contenido del correo no fue recibido en formato bytes."
        )

    mensaje = email.message_from_bytes(correo_bytes, policy=policy.default)
    if not isinstance(mensaje, EmailMessage):
        raise RuntimeError(
            "Python no pudo convertir el correo en un EmailMessage."
        )
    return mensaje


def obtener_datos_correo(mensaje: EmailMessage) -> dict[str, str]:
    """Extraer los encabezados que necesita el flujo actual."""

    return {
        "Subject": str(mensaje.get("Subject", "Sin asunto")),
        "From": str(mensaje.get("From", "Remitente no informado")),
        "To": str(mensaje.get("To", "Destinatario no informado")),
        "Date": str(mensaje.get("Date", "Fecha no informada")),
    }
