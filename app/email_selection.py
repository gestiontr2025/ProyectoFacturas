"""Reglas para decidir qué correos serán procesados.

La selección está aislada porque es una regla de negocio sencilla y fácil de
probar sin conectarse a Gmail.
"""

def seleccionar_correos_recientes(
    identificadores_correos,
    limite
):
    """
    Seleccionar los correos más recientes.

    Parámetros
    ----------
    identificadores_correos:
        Lista completa de identificadores IMAP.

    limite:
        Cantidad máxima de correos que serán procesados.

    Retorna
    -------
    list
        Lista de identificadores ordenada desde el correo
        más reciente hasta el más antiguo.
    """

    if not isinstance(limite, int):

        raise TypeError(
            "EMAIL_PROCESSING_LIMIT debe ser un número "
            "entero."
        )

    if limite <= 0:

        raise ValueError(
            "EMAIL_PROCESSING_LIMIT debe ser mayor que cero."
        )

    correos_recientes = identificadores_correos[
        -limite:
    ]

    correos_recientes = list(
        reversed(correos_recientes)
    )

    return correos_recientes

