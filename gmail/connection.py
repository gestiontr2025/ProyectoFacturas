"""Creación de la conexión autenticada con Gmail.

Este módulo conoce los datos técnicos necesarios para conectarse al servidor
IMAP de Gmail. No busca correos ni interpreta mensajes: su única tarea es
entregar una conexión lista para usar.
"""

import imaplib

import config


GMAIL_IMAP_SERVER = "imap.gmail.com"


def conectar() -> imaplib.IMAP4_SSL:
    """Abrir una conexión segura e iniciar sesión en Gmail.

    Returns:
        Una conexión IMAP autenticada.

    Raises:
        imaplib.IMAP4.error:
            Si Gmail rechaza las credenciales o la autenticación.
        OSError:
            Si existe un problema de red.

    Por qué esta función devuelve la conexión:
        Las demás etapas necesitan reutilizar la misma sesión para buscar y
        leer varios correos. Abrir una conexión nueva por cada mensaje sería
        más lento y dificultaría cerrar correctamente la sesión.
    """

    print()
    print("--------------------------------")
    print("Conectando con Gmail...")
    print("--------------------------------")

    conexion = imaplib.IMAP4_SSL(GMAIL_IMAP_SERVER)
    conexion.login(config.EMAIL, config.APP_PASSWORD)

    print("Conexión realizada correctamente.")
    return conexion
