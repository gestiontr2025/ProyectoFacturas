"""
==========================================================
PROYECTO
==========================================================

Proyecto Facturas

Versión
--------
0.9

Archivo
--------
file_manager.py

Descripción
-----------
Este módulo contiene las funciones relacionadas con el
sistema de archivos.

Sus responsabilidades actuales son:

- Crear la carpeta principal de destino.
- Determinar si un archivo adjunto es un PDF.
- Filtrar los adjuntos que no sean PDF.
- Comprobar si un archivo ya fue guardado.
- Evitar guardar archivos duplicados.
- Obtener el contenido binario de los adjuntos.
- Guardar los archivos PDF.
- Devolver las rutas de los archivos realmente guardados.

Separar estas tareas de gmail_client.py permite que cada
módulo tenga una responsabilidad clara.

gmail_client.py se ocupa de Gmail.

file_manager.py se ocupa de la validación y del guardado de
los archivos.

Autor
------
Diego (desarrollador del proyecto)
ChatGPT (mentor técnico)

==========================================================
"""


# ==========================================================
# INICIO DEL BLOQUE DE IMPORTACIONES
# ==========================================================

from pathlib import Path

# ==========================================================
# FIN DEL BLOQUE DE IMPORTACIONES
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN preparar_carpeta_destino()
# ==========================================================

def preparar_carpeta_destino(carpeta_destino):
    """
    Crear la carpeta donde se guardarán los archivos.

    Parámetros
    ----------
    carpeta_destino:

        Ruta de la carpeta que deseamos crear.

    Retorna
    -------
    Path

        Ruta convertida en un objeto Path.

    Funcionamiento
    --------------
    parents=True permite crear las carpetas superiores que
    puedan faltar.

    exist_ok=True evita que se produzca un error si la
    carpeta ya existe.
    """

    carpeta_destino = Path(
        carpeta_destino
    )

    carpeta_destino.mkdir(
        parents=True,
        exist_ok=True
    )

    return carpeta_destino

# ==========================================================
# FIN DE LA FUNCIÓN preparar_carpeta_destino()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN es_archivo_pdf()
# ==========================================================

def es_archivo_pdf(adjunto):
    """
    Determinar si un archivo adjunto debe considerarse PDF.

    Parámetros
    ----------
    adjunto:

        Diccionario creado por:

            gmail_client.obtener_adjuntos()

        Su estructura esperada es:

            {
                "nombre": "...",
                "tipo_contenido": "...",
                "parte": parte_mime
            }

    Retorna
    -------
    bool

        True si el archivo parece ser un PDF.

        False si el archivo no parece ser un PDF.

    Criterios utilizados
    --------------------
    Un adjunto será considerado PDF cuando se cumpla al
    menos una de estas condiciones:

    1. Su tipo MIME sea application/pdf.

    2. Su nombre termine con la extensión .pdf.
    """

    nombre_archivo = adjunto.get(
        "nombre",
        ""
    )

    tipo_contenido = adjunto.get(
        "tipo_contenido",
        ""
    )

    nombre_archivo = str(
        nombre_archivo
    ).lower()

    tipo_contenido = str(
        tipo_contenido
    ).lower()

    tiene_tipo_mime_pdf = (
        tipo_contenido == "application/pdf"
    )

    tiene_extension_pdf = nombre_archivo.endswith(
        ".pdf"
    )

    return (
        tiene_tipo_mime_pdf
        or
        tiene_extension_pdf
    )

# ==========================================================
# FIN DE LA FUNCIÓN es_archivo_pdf()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN filtrar_archivos_pdf()
# ==========================================================

def filtrar_archivos_pdf(adjuntos):
    """
    Obtener únicamente los adjuntos que sean archivos PDF.

    Parámetros
    ----------
    adjuntos:

        Lista de adjuntos devuelta por:

            gmail_client.obtener_adjuntos()

    Retorna
    -------
    list

        Nueva lista que contiene solamente los adjuntos PDF.

    Importante
    ----------
    Esta función no modifica la lista original.
    """

    archivos_pdf = []

    for adjunto in adjuntos:

        if es_archivo_pdf(adjunto):

            archivos_pdf.append(
                adjunto
            )

    return archivos_pdf

# ==========================================================
# FIN DE LA FUNCIÓN filtrar_archivos_pdf()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN construir_ruta_archivo()
# ==========================================================

def construir_ruta_archivo(
    carpeta_destino,
    nombre_archivo
):
    """
    Construir la ruta completa de un archivo.

    Parámetros
    ----------
    carpeta_destino:

        Carpeta donde debería guardarse el archivo.

    nombre_archivo:

        Nombre original del archivo adjunto.

    Retorna
    -------
    Path

        Ruta completa formada por la carpeta de destino y el
        nombre del archivo.

    Ejemplo
    -------
    Si recibimos:

        carpeta_destino:

            C:\\Facturas

        nombre_archivo:

            factura.pdf

    la función devolverá:

        C:\\Facturas\\factura.pdf
    """

    carpeta_destino = Path(
        carpeta_destino
    )

    ruta_archivo = (
        carpeta_destino / nombre_archivo
    )

    return ruta_archivo

# ==========================================================
# FIN DE LA FUNCIÓN construir_ruta_archivo()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN archivo_ya_existe()
# ==========================================================

def archivo_ya_existe(
    carpeta_destino,
    nombre_archivo
):
    """
    Comprobar si un archivo ya existe en la carpeta.

    Parámetros
    ----------
    carpeta_destino:

        Carpeta donde se desea guardar el archivo.

    nombre_archivo:

        Nombre del archivo que deseamos comprobar.

    Retorna
    -------
    bool

        True si el archivo ya existe.

        False si el archivo todavía no existe.

    Importante
    ----------
    En esta primera versión de la detección de duplicados,
    dos archivos se consideran iguales cuando tienen
    exactamente el mismo nombre dentro de la misma carpeta.

    Más adelante podremos mejorar esta validación comparando
    también el contenido de los archivos.
    """

    ruta_archivo = construir_ruta_archivo(
        carpeta_destino,
        nombre_archivo
    )

    return ruta_archivo.exists()

# ==========================================================
# FIN DE LA FUNCIÓN archivo_ya_existe()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN guardar_adjunto()
# ==========================================================

def guardar_adjunto(adjunto, carpeta_destino):
    """
    Guardar un único archivo adjunto si todavía no existe.

    Parámetros
    ----------
    adjunto:

        Diccionario creado por:

            gmail_client.obtener_adjuntos()

        Su estructura es:

            {
                "nombre": "...",
                "tipo_contenido": "...",
                "parte": parte_mime
            }

    carpeta_destino:

        Carpeta donde se guardará el archivo.

    Retorna
    -------
    Path | None

        Devuelve un objeto Path si el archivo fue guardado.

        Devuelve None si el archivo ya existía y, por lo
        tanto, no fue guardado nuevamente.
    """

    nombre_archivo = adjunto["nombre"]

    # ------------------------------------------------------
    # Antes de recuperar el contenido binario, comprobamos si
    # el archivo ya existe.
    #
    # De esta manera evitamos realizar trabajo innecesario.
    # ------------------------------------------------------

    if archivo_ya_existe(
        carpeta_destino,
        nombre_archivo
    ):
        return None

    parte = adjunto["parte"]

    contenido_archivo = parte.get_payload(
        decode=True
    )

    if contenido_archivo is None:
        raise ValueError(
            "No fue posible obtener el contenido del "
            f"archivo adjunto: {nombre_archivo}"
        )

    ruta_destino = construir_ruta_archivo(
        carpeta_destino,
        nombre_archivo
    )

    ruta_destino.write_bytes(
        contenido_archivo
    )

    return ruta_destino

# ==========================================================
# FIN DE LA FUNCIÓN guardar_adjunto()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN guardar_adjuntos()
# ==========================================================

def guardar_adjuntos(adjuntos, carpeta_destino):
    """
    Filtrar y guardar únicamente los archivos PDF nuevos.

    Parámetros
    ----------
    adjuntos:

        Lista devuelta por:

            gmail_client.obtener_adjuntos()

    carpeta_destino:

        Ruta principal donde se guardarán los archivos PDF.

    Retorna
    -------
    list

        Lista de objetos Path.

        Cada Path representa un archivo PDF que fue guardado
        durante la ejecución actual.

        Los archivos que ya existían no aparecen en esta
        lista.

        Si no se guarda ningún archivo, devuelve una lista
        vacía.
    """

    archivos_pdf = filtrar_archivos_pdf(
        adjuntos
    )

    if not archivos_pdf:
        return []

    carpeta_destino = preparar_carpeta_destino(
        carpeta_destino
    )

    archivos_guardados = []

    for adjunto in archivos_pdf:

        ruta_guardada = guardar_adjunto(
            adjunto,
            carpeta_destino
        )

        # --------------------------------------------------
        # guardar_adjunto() devuelve None cuando el archivo
        # ya existía.
        #
        # Solo agregamos la ruta si realmente se guardó un
        # archivo nuevo.
        # --------------------------------------------------

        if ruta_guardada is not None:

            archivos_guardados.append(
                ruta_guardada
            )

    return archivos_guardados

# ==========================================================
# FIN DE LA FUNCIÓN guardar_adjuntos()
# ==========================================================


# ==========================================================
# FIN DEL ARCHIVO
# ==========================================================