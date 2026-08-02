"""Localización y selección de carpetas de Gmail.

Gmail traduce algunos nombres de carpetas según el idioma de la cuenta. Por
eso no conviene escribir ``[Gmail]/Todos`` directamente en el código: una
cuenta configurada en inglés puede exponer ``[Gmail]/All Mail``.
"""

import imaplib
import re


NOMBRES_CARPETA_TODOS = ("todos", "all mail")


def encontrar_carpeta_todos(conexion: imaplib.IMAP4_SSL) -> str:
    """Encontrar la carpeta que contiene todos los mensajes de Gmail.

    Args:
        conexion:
            Sesión IMAP autenticada.

    Returns:
        El nombre exacto de la carpeta tal como lo informa Gmail.

    Raises:
        RuntimeError:
            Si Gmail no entrega una lista válida o no se reconoce la carpeta.
    """

    estado, carpetas = conexion.list()

    if estado != "OK":
        raise RuntimeError(
            "Gmail no permitió obtener la lista de carpetas."
        )

    if not carpetas:
        raise RuntimeError(
            "Gmail devolvió una lista de carpetas vacía."
        )

    for carpeta_bytes in carpetas:
        nombre = _extraer_nombre_carpeta_todos(carpeta_bytes)

        if nombre is None:
            continue

        print()
        print("--------------------------------")
        print("Carpeta de todos los correos encontrada:")
        print(nombre)
        print("--------------------------------")
        return nombre

    raise RuntimeError(
        "No fue posible encontrar la carpeta que contiene todos los correos."
    )


def _extraer_nombre_carpeta_todos(carpeta_bytes: object) -> str | None:
    """Interpretar una línea de la respuesta IMAP.

    Esta función es interna, por eso su nombre comienza con ``_``. Separarla
    permite probar la interpretación de carpetas sin conectarnos realmente a
    Gmail.
    """

    if not isinstance(carpeta_bytes, bytes):
        return None

    carpeta_texto = carpeta_bytes.decode("utf-8", errors="replace")
    carpeta_minusculas = carpeta_texto.lower()

    if not any(
        nombre in carpeta_minusculas
        for nombre in NOMBRES_CARPETA_TODOS
    ):
        return None

    # Gmail suele envolver el nombre de la carpeta entre comillas. Buscamos el
    # último texto entre comillas porque nombres como ``All Mail`` contienen un
    # espacio y no pueden separarse correctamente con un simple ``split``.
    nombres_entre_comillas = re.findall(r'"([^"\r\n]+)"', carpeta_texto)

    if nombres_entre_comillas:
        return nombres_entre_comillas[-1]

    # Algunas implementaciones IMAP pueden devolver el nombre sin comillas.
    # En ese caso conservamos el último elemento como alternativa.
    partes = carpeta_texto.rsplit(" ", 1)
    return partes[-1] if len(partes) == 2 else None
