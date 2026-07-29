"""
==========================================================
PROYECTO
==========================================================

Proyecto Facturas

Versión
--------
0.8

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
- Obtener el contenido binario de los adjuntos.
- Guardar los archivos PDF.
- Evitar sobrescribir archivos existentes.
- Devolver las rutas de los archivos guardados.

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


# ----------------------------------------------------------
# Importamos Path desde pathlib.
#
# Path permite trabajar con rutas de archivos y carpetas de
# una manera moderna y compatible con distintos sistemas
# operativos.
# ----------------------------------------------------------

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

        En nuestro proyecto será:

            config.SAVE_FOLDER

    Retorna
    -------
    Path

        Devuelve la ruta convertida en un objeto Path.

    Funcionamiento
    --------------
    mkdir() crea una carpeta.

    parents=True permite crear también las carpetas
    superiores que puedan faltar.

    exist_ok=True evita que aparezca un error si la carpeta
    ya existe.
    """

    # ------------------------------------------------------
    # Convertimos el valor recibido en un objeto Path.
    #
    # Aunque config.SAVE_FOLDER ya es un Path, esta
    # conversión hace que la función también pueda recibir
    # una ruta escrita como texto.
    # ------------------------------------------------------

    carpeta_destino = Path(carpeta_destino)


    # ------------------------------------------------------
    # Creamos la carpeta.
    #
    # parents=True:
    #
    #     Crea también las carpetas superiores necesarias.
    #
    # exist_ok=True:
    #
    #     No produce un error si la carpeta ya existe.
    # ------------------------------------------------------

    carpeta_destino.mkdir(
        parents=True,
        exist_ok=True
    )


    # ------------------------------------------------------
    # Devolvemos la ruta preparada.
    # ------------------------------------------------------

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

        Devuelve True si el archivo parece ser un PDF.

        Devuelve False si el archivo no parece ser un PDF.

    Criterios utilizados
    --------------------
    Un archivo será considerado PDF cuando se cumpla al
    menos una de estas condiciones:

    1. Su tipo de contenido MIME sea:

           application/pdf

    2. Su nombre termine con la extensión:

           .pdf

    Utilizamos ambas comprobaciones porque algunos correos
    pueden informar incorrectamente el tipo MIME del archivo.
    """

    # ------------------------------------------------------
    # Obtenemos el nombre del archivo.
    #
    # get() permite proporcionar un valor predeterminado si
    # la clave no existe.
    #
    # En este caso utilizamos una cadena vacía.
    # ------------------------------------------------------

    nombre_archivo = adjunto.get(
        "nombre",
        ""
    )


    # ------------------------------------------------------
    # Obtenemos el tipo MIME informado por el correo.
    #
    # Un PDF normalmente utiliza:
    #
    #     application/pdf
    # ------------------------------------------------------

    tipo_contenido = adjunto.get(
        "tipo_contenido",
        ""
    )


    # ------------------------------------------------------
    # Convertimos ambos valores a texto.
    #
    # Esto evita errores en caso de que alguno de los datos
    # recibidos sea None u otro tipo de valor.
    # ------------------------------------------------------

    nombre_archivo = str(
        nombre_archivo
    )

    tipo_contenido = str(
        tipo_contenido
    )


    # ------------------------------------------------------
    # lower() convierte el texto a minúsculas.
    #
    # Esto permite reconocer todas estas variantes:
    #
    #     factura.pdf
    #     factura.PDF
    #     factura.Pdf
    # ------------------------------------------------------

    nombre_archivo = nombre_archivo.lower()

    tipo_contenido = tipo_contenido.lower()


    # ------------------------------------------------------
    # Primera comprobación:
    #
    # Verificamos si el servidor declaró que el archivo
    # utiliza el tipo MIME application/pdf.
    # ------------------------------------------------------

    tiene_tipo_mime_pdf = (
        tipo_contenido == "application/pdf"
    )


    # ------------------------------------------------------
    # Segunda comprobación:
    #
    # endswith(".pdf") verifica si el nombre termina con la
    # extensión .pdf.
    # ------------------------------------------------------

    tiene_extension_pdf = nombre_archivo.endswith(
        ".pdf"
    )


    # ------------------------------------------------------
    # El operador or devuelve True cuando al menos una de
    # las dos condiciones es verdadera.
    #
    # De esta forma aceptamos:
    #
    # - Archivos con tipo MIME correcto.
    # - Archivos con extensión correcta.
    #
    # Esto nos protege frente a correos cuyo tipo MIME haya
    # sido configurado incorrectamente.
    # ------------------------------------------------------

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

        Nueva lista que contiene solamente los adjuntos
        considerados PDF.

    Importante
    ----------
    Esta función no modifica la lista original.

    Crea y devuelve una lista nueva.
    """

    # ------------------------------------------------------
    # Creamos una lista vacía.
    #
    # Dentro de ella agregaremos solamente los archivos que
    # superen la validación de es_archivo_pdf().
    # ------------------------------------------------------

    archivos_pdf = []


    # ------------------------------------------------------
    # Recorremos todos los adjuntos recibidos.
    # ------------------------------------------------------

    for adjunto in adjuntos:

        # --------------------------------------------------
        # Consultamos si el adjunto actual es un PDF.
        # --------------------------------------------------

        if es_archivo_pdf(adjunto):

            # ----------------------------------------------
            # Si la condición devuelve True, agregamos el
            # adjunto a la nueva lista.
            # ----------------------------------------------

            archivos_pdf.append(
                adjunto
            )


    # ------------------------------------------------------
    # Devolvemos únicamente los archivos PDF.
    # ------------------------------------------------------

    return archivos_pdf

# ==========================================================
# FIN DE LA FUNCIÓN filtrar_archivos_pdf()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN obtener_ruta_disponible()
# ==========================================================

def obtener_ruta_disponible(carpeta_destino, nombre_archivo):
    """
    Crear una ruta que no sobrescriba archivos existentes.

    Parámetros
    ----------
    carpeta_destino:

        Carpeta donde se desea guardar el archivo.

    nombre_archivo:

        Nombre original del adjunto.

    Retorna
    -------
    Path

        Ruta disponible para guardar el archivo.

    Ejemplo
    -------
    Supongamos que ya existe:

        factura.pdf

    La función devolverá:

        factura_1.pdf

    Si también existe factura_1.pdf, devolverá:

        factura_2.pdf
    """

    carpeta_destino = Path(carpeta_destino)


    # ------------------------------------------------------
    # Construimos inicialmente la ruta utilizando el nombre
    # original.
    # ------------------------------------------------------

    ruta_archivo = carpeta_destino / nombre_archivo


    # ------------------------------------------------------
    # Si la ruta todavía no existe, podemos utilizarla.
    # ------------------------------------------------------

    if not ruta_archivo.exists():
        return ruta_archivo


    # ------------------------------------------------------
    # Path.stem contiene el nombre sin la extensión.
    #
    # Ejemplo:
    #
    #     factura.pdf
    #
    # stem:
    #
    #     factura
    # ------------------------------------------------------

    nombre_sin_extension = ruta_archivo.stem


    # ------------------------------------------------------
    # Path.suffix contiene la extensión.
    #
    # Ejemplo:
    #
    #     .pdf
    # ------------------------------------------------------

    extension = ruta_archivo.suffix


    # ------------------------------------------------------
    # Comenzamos a buscar nombres alternativos desde 1.
    # ------------------------------------------------------

    numero_copia = 1


    # ------------------------------------------------------
    # while True crea un ciclo que continúa hasta encontrar
    # una ruta disponible.
    #
    # La función finalizará cuando ejecute return.
    # ------------------------------------------------------

    while True:

        nombre_alternativo = (
            f"{nombre_sin_extension}_{numero_copia}"
            f"{extension}"
        )

        ruta_alternativa = (
            carpeta_destino / nombre_alternativo
        )


        # --------------------------------------------------
        # Si la ruta alternativa no existe, la devolvemos.
        # --------------------------------------------------

        if not ruta_alternativa.exists():
            return ruta_alternativa


        # --------------------------------------------------
        # Si ya existe, aumentamos el número y probamos otra
        # vez.
        # --------------------------------------------------

        numero_copia += 1

# ==========================================================
# FIN DE LA FUNCIÓN obtener_ruta_disponible()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN guardar_adjunto()
# ==========================================================

def guardar_adjunto(adjunto, carpeta_destino):
    """
    Guardar un único archivo adjunto.

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
    Path

        Ruta final del archivo guardado.
    """

    # ------------------------------------------------------
    # Obtenemos el nombre del archivo.
    # ------------------------------------------------------

    nombre_archivo = adjunto["nombre"]


    # ------------------------------------------------------
    # Obtenemos la parte MIME.
    #
    # La parte MIME contiene tanto la información técnica
    # como el contenido real del adjunto.
    # ------------------------------------------------------

    parte = adjunto["parte"]


    # ------------------------------------------------------
    # get_payload(decode=True) recupera el contenido real del
    # adjunto y lo convierte en bytes.
    #
    # Los bytes representan el contenido binario del archivo.
    #
    # Los PDF, imágenes y otros archivos no se guardan como
    # texto normal: se guardan como datos binarios.
    # ------------------------------------------------------

    contenido_archivo = parte.get_payload(
        decode=True
    )


    # ------------------------------------------------------
    # Validamos que realmente hayamos obtenido contenido.
    # ------------------------------------------------------

    if contenido_archivo is None:
        raise ValueError(
            "No fue posible obtener el contenido del "
            f"archivo adjunto: {nombre_archivo}"
        )


    # ------------------------------------------------------
    # Obtenemos una ruta que no sobrescriba otro archivo.
    # ------------------------------------------------------

    ruta_destino = obtener_ruta_disponible(
        carpeta_destino,
        nombre_archivo
    )


    # ------------------------------------------------------
    # write_bytes() crea el archivo y escribe los bytes.
    #
    # Es equivalente a abrir el archivo en modo binario:
    #
    #     open(ruta, "wb")
    #
    # pero Path proporciona una sintaxis más sencilla.
    # ------------------------------------------------------

    ruta_destino.write_bytes(
        contenido_archivo
    )


    # ------------------------------------------------------
    # Devolvemos la ubicación final del archivo.
    # ------------------------------------------------------

    return ruta_destino

# ==========================================================
# FIN DE LA FUNCIÓN guardar_adjunto()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN guardar_adjuntos()
# ==========================================================

def guardar_adjuntos(adjuntos, carpeta_destino):
    """
    Filtrar y guardar únicamente los archivos PDF recibidos.

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

        Cada Path representa un archivo PDF guardado.

        Si no se encuentra ningún PDF, devuelve una lista
        vacía.
    """

    # ------------------------------------------------------
    # Filtramos los adjuntos antes de crear archivos.
    #
    # La variable archivos_pdf contendrá solamente aquellos
    # adjuntos que hayan superado la validación.
    # ------------------------------------------------------

    archivos_pdf = filtrar_archivos_pdf(
        adjuntos
    )


    # ------------------------------------------------------
    # Si no encontramos ningún PDF, devolvemos inmediatamente
    # una lista vacía.
    #
    # En este caso no es necesario crear la carpeta.
    # ------------------------------------------------------

    if not archivos_pdf:
        return []


    # ------------------------------------------------------
    # Nos aseguramos de que la carpeta de destino exista.
    # ------------------------------------------------------

    carpeta_destino = preparar_carpeta_destino(
        carpeta_destino
    )


    # ------------------------------------------------------
    # Creamos una lista vacía.
    #
    # Dentro de ella guardaremos las rutas finales.
    # ------------------------------------------------------

    archivos_guardados = []


    # ------------------------------------------------------
    # Recorremos únicamente los adjuntos PDF.
    #
    # Los adjuntos de otros tipos ya quedaron fuera de esta
    # lista y no serán guardados.
    # ------------------------------------------------------

    for adjunto in archivos_pdf:

        # --------------------------------------------------
        # Guardamos el PDF actual.
        # --------------------------------------------------

        ruta_guardada = guardar_adjunto(
            adjunto,
            carpeta_destino
        )


        # --------------------------------------------------
        # Agregamos su ruta a la lista.
        # --------------------------------------------------

        archivos_guardados.append(
            ruta_guardada
        )


    # ------------------------------------------------------
    # Devolvemos todas las rutas de los PDF guardados.
    # ------------------------------------------------------

    return archivos_guardados

# ==========================================================
# FIN DE LA FUNCIÓN guardar_adjuntos()
# ==========================================================


# ==========================================================
# FIN DEL ARCHIVO
# ==========================================================