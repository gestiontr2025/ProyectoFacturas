"""
==========================================================
PROYECTO
==========================================================

Proyecto Facturas

Versión
--------
0.7

Archivo
--------
file_manager.py

Descripción
-----------
Este módulo contiene las funciones relacionadas con el
sistema de archivos.

Sus responsabilidades actuales son:

- Crear la carpeta principal de destino.
- Obtener el contenido binario de los adjuntos.
- Guardar los archivos adjuntos.
- Evitar sobrescribir archivos existentes.
- Devolver las rutas de los archivos guardados.

Separar estas tareas de gmail_client.py permite que cada
módulo tenga una responsabilidad clara.

gmail_client.py se ocupa de Gmail.

file_manager.py se ocupa de carpetas y archivos.

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
    Guardar todos los archivos adjuntos recibidos.

    Parámetros
    ----------
    adjuntos:

        Lista devuelta por:

            gmail_client.obtener_adjuntos()

    carpeta_destino:

        Ruta principal donde se guardarán los archivos.

    Retorna
    -------
    list

        Lista de objetos Path.

        Cada Path representa un archivo guardado.
    """

    # ------------------------------------------------------
    # Primero nos aseguramos de que la carpeta exista.
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
    # Recorremos todos los adjuntos detectados.
    # ------------------------------------------------------

    for adjunto in adjuntos:

        # --------------------------------------------------
        # Guardamos el adjunto actual.
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
    # Devolvemos todas las rutas.
    # ------------------------------------------------------

    return archivos_guardados

# ==========================================================
# FIN DE LA FUNCIÓN guardar_adjuntos()
# ==========================================================


# ==========================================================
# FIN DEL ARCHIVO
# ==========================================================