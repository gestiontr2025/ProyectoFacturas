"""
==========================================================
PROYECTO
==========================================================

Proyecto Facturas

Archivo
-------
pdf_reader.py

Descripción
-----------
Este módulo contiene las funciones relacionadas con la
lectura del contenido interno de archivos PDF.

Su responsabilidad principal es:

- Recibir la ruta de un archivo PDF.
- Validar que la ruta sea correcta.
- Abrir el documento.
- Determinar cuántas páginas contiene.
- Extraer el texto de cada página.
- Unir el texto de todas las páginas.
- Detectar documentos que no contienen texto extraíble.
- Devolver los resultados sin imprimirlos directamente.

Separar estas tareas en un módulo independiente permite
mantener una responsabilidad clara dentro del proyecto.

Distribución actual de responsabilidades
----------------------------------------
gmail_client.py:

    Se conecta con Gmail y obtiene los correos y adjuntos.

file_manager.py:

    Valida, filtra y guarda los archivos PDF.

invoice_organizer.py:

    Construye las carpetas donde se guardan las facturas.

pdf_reader.py:

    Abre los PDF ya guardados y extrae su contenido textual.

console_output.py:

    Centraliza la información mostrada en la consola.

main.py:

    Coordina el funcionamiento general del programa.

Limitaciones
------------
Esta primera versión solamente puede extraer texto que se
encuentre almacenado como caracteres dentro del PDF.

Algunos documentos son imágenes escaneadas guardadas dentro
de un archivo PDF.

Esos documentos pueden verse correctamente al abrirlos, pero
no necesariamente contienen texto extraíble.

Para interpretar archivos escaneados será necesario agregar
OCR en una versión futura.

Este módulo no debe
-------------------
- Conectarse con Gmail.
- Descargar archivos.
- Crear carpetas de facturas.
- Detectar proveedores.
- Exportar información a Excel.
- Imprimir directamente los resultados en la consola.
- Modificar el contenido de los documentos.

Autor
-----
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
# Path permite trabajar con rutas de archivos de una manera
# moderna, clara y compatible con distintos sistemas
# operativos.
# ----------------------------------------------------------

from pathlib import Path


# ----------------------------------------------------------
# Importamos PdfReader desde la biblioteca pypdf.
#
# PdfReader se encarga de abrir e interpretar la estructura
# interna de los documentos PDF.
#
# La biblioteca puede instalarse con:
#
#     python -m pip install pypdf
# ----------------------------------------------------------

from pypdf import PdfReader


# ----------------------------------------------------------
# Importamos PdfReadError.
#
# Esta excepción puede producirse cuando pypdf intenta abrir
# un archivo cuya estructura PDF es inválida, incompleta o
# está dañada.
#
# Importarla nos permite transformar ese error técnico en un
# mensaje más comprensible para el programa.
# ----------------------------------------------------------

from pypdf.errors import PdfReadError

# ==========================================================
# FIN DEL BLOQUE DE IMPORTACIONES
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN validar_ruta_pdf()
# ==========================================================

def validar_ruta_pdf(ruta_pdf):
    """
    Validar que una ruta corresponda a un archivo PDF válido.

    Parámetros
    ----------
    ruta_pdf:

        Ruta del archivo que deseamos leer.

        Puede recibirse como:

        - Una cadena de texto.
        - Un objeto Path.

    Retorna
    -------
    Path

        Ruta convertida en un objeto Path después de superar
        todas las validaciones.

    Excepciones
    -----------
    ValueError:

        Se produce si la ruta está vacía o si la extensión
        del archivo no es .pdf.

    FileNotFoundError:

        Se produce si el archivo no existe.

    IsADirectoryError:

        Se produce si la ruta corresponde a una carpeta en
        lugar de un archivo.
    """

    # ------------------------------------------------------
    # Comprobamos primero que se haya recibido algún valor.
    #
    # Esto evita convertir accidentalmente una cadena vacía
    # en una ruta que apunte a la carpeta actual.
    # ------------------------------------------------------

    if ruta_pdf is None:

        raise ValueError(
            "No se recibió una ruta para leer el archivo PDF."
        )

    # ------------------------------------------------------
    # Convertimos el valor a texto para detectar cadenas
    # vacías o compuestas solamente por espacios.
    # ------------------------------------------------------

    ruta_como_texto = str(
        ruta_pdf
    ).strip()

    if not ruta_como_texto:

        raise ValueError(
            "La ruta del archivo PDF no puede estar vacía."
        )

    # ------------------------------------------------------
    # Convertimos la ruta recibida en un objeto Path.
    # ------------------------------------------------------

    ruta_pdf = Path(
        ruta_como_texto
    )

    # ------------------------------------------------------
    # Verificamos que la ruta exista.
    # ------------------------------------------------------

    if not ruta_pdf.exists():

        raise FileNotFoundError(
            "No se encontró el archivo PDF indicado: "
            f"{ruta_pdf}"
        )

    # ------------------------------------------------------
    # Una ruta existente puede representar un archivo o una
    # carpeta.
    #
    # is_file() debe devolver True para continuar.
    # ------------------------------------------------------

    if not ruta_pdf.is_file():

        raise IsADirectoryError(
            "La ruta indicada no corresponde a un archivo: "
            f"{ruta_pdf}"
        )

    # ------------------------------------------------------
    # Comprobamos la extensión sin distinguir entre
    # mayúsculas y minúsculas.
    #
    # Por lo tanto, se aceptan tanto:
    #
    #     factura.pdf
    #
    # como:
    #
    #     FACTURA.PDF
    # ------------------------------------------------------

    if ruta_pdf.suffix.lower() != ".pdf":

        raise ValueError(
            "El archivo indicado no posee extensión PDF: "
            f"{ruta_pdf.name}"
        )

    return ruta_pdf

# ==========================================================
# FIN DE LA FUNCIÓN validar_ruta_pdf()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN abrir_pdf()
# ==========================================================

def abrir_pdf(ruta_pdf):
    """
    Abrir un archivo PDF después de validar su ruta.

    Parámetros
    ----------
    ruta_pdf:

        Ruta del documento que deseamos abrir.

    Retorna
    -------
    PdfReader

        Objeto utilizado por pypdf para acceder al contenido
        y a las páginas del documento.

    Excepciones
    -----------
    ValueError:

        Puede producirse si el archivo está protegido con una
        contraseña que no permite abrirlo automáticamente.

    PdfReadError:

        Puede producirse si el documento no posee una
        estructura PDF válida.
    """

    ruta_pdf = validar_ruta_pdf(
        ruta_pdf
    )

    try:

        lector = PdfReader(
            ruta_pdf
        )

    except PdfReadError as error:

        raise PdfReadError(
            "No fue posible interpretar el archivo PDF. "
            "El documento puede estar dañado o tener una "
            "estructura inválida. "
            f"Archivo: {ruta_pdf}"
        ) from error

    # ------------------------------------------------------
    # Algunos documentos PDF se encuentran cifrados.
    #
    # En ciertos casos pueden abrirse utilizando una
    # contraseña vacía.
    #
    # Si eso no funciona, informamos que el documento está
    # protegido y no puede leerse automáticamente.
    # ------------------------------------------------------

    if lector.is_encrypted:

        try:

            resultado_desbloqueo = lector.decrypt(
                ""
            )

        except Exception as error:

            raise ValueError(
                "El archivo PDF está protegido y no fue "
                "posible desbloquearlo automáticamente. "
                f"Archivo: {ruta_pdf}"
            ) from error

        if resultado_desbloqueo == 0:

            raise ValueError(
                "El archivo PDF requiere una contraseña. "
                f"Archivo: {ruta_pdf}"
            )

    return lector

# ==========================================================
# FIN DE LA FUNCIÓN abrir_pdf()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN extraer_texto_pagina()
# ==========================================================

def extraer_texto_pagina(pagina):
    """
    Extraer el texto de una página individual.

    Parámetros
    ----------
    pagina:

        Página perteneciente a un objeto PdfReader.

    Retorna
    -------
    str

        Texto extraído de la página.

        Si la página no contiene texto extraíble, devuelve
        una cadena vacía.
    """

    texto_pagina = pagina.extract_text()

    # ------------------------------------------------------
    # extract_text() puede devolver None cuando no encuentra
    # texto extraíble.
    #
    # Para que el resto del programa siempre trabaje con
    # cadenas, reemplazamos None por una cadena vacía.
    # ------------------------------------------------------

    if texto_pagina is None:

        return ""

    # ------------------------------------------------------
    # Eliminamos espacios y saltos de línea sobrantes al
    # comienzo y al final.
    #
    # No alteramos el contenido interno del texto.
    # ------------------------------------------------------

    texto_pagina = texto_pagina.strip()

    return texto_pagina

# ==========================================================
# FIN DE LA FUNCIÓN extraer_texto_pagina()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN extraer_paginas_pdf()
# ==========================================================

def extraer_paginas_pdf(ruta_pdf):
    """
    Extraer por separado el texto de todas las páginas.

    Parámetros
    ----------
    ruta_pdf:

        Ruta del documento PDF.

    Retorna
    -------
    list

        Lista de diccionarios.

        Cada diccionario representa una página y posee esta
        estructura:

            {
                "numero": 1,
                "texto": "Contenido de la página"
            }

        Si una página no contiene texto extraíble, su valor
        "texto" será una cadena vacía.
    """

    lector = abrir_pdf(
        ruta_pdf
    )

    paginas_extraidas = []

    for numero_pagina, pagina in enumerate(
        lector.pages,
        start=1
    ):

        try:

            texto_pagina = extraer_texto_pagina(
                pagina
            )

        except Exception as error:

            raise ValueError(
                "Se produjo un error al extraer el texto de "
                f"la página {numero_pagina}."
            ) from error

        informacion_pagina = {
            "numero": numero_pagina,
            "texto": texto_pagina
        }

        paginas_extraidas.append(
            informacion_pagina
        )

    return paginas_extraidas

# ==========================================================
# FIN DE LA FUNCIÓN extraer_paginas_pdf()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN unir_texto_paginas()
# ==========================================================

def unir_texto_paginas(paginas):
    """
    Unir el texto extraído de todas las páginas.

    Parámetros
    ----------
    paginas:

        Lista de diccionarios generada por:

            extraer_paginas_pdf()

    Retorna
    -------
    str

        Texto completo del documento.

        Las páginas que contienen texto se separan mediante
        dos saltos de línea.

        Las páginas vacías no agregan espacios innecesarios.
    """

    textos_disponibles = []

    for pagina in paginas:

        texto_pagina = pagina.get(
            "texto",
            ""
        )

        if texto_pagina:

            textos_disponibles.append(
                texto_pagina
            )

    texto_completo = "\n\n".join(
        textos_disponibles
    )

    return texto_completo

# ==========================================================
# FIN DE LA FUNCIÓN unir_texto_paginas()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN leer_pdf()
# ==========================================================

def leer_pdf(ruta_pdf):
    """
    Leer un archivo PDF y devolver un resumen de su contenido.

    Parámetros
    ----------
    ruta_pdf:

        Ruta del archivo que deseamos procesar.

    Retorna
    -------
    dict

        Diccionario con la información obtenida.

        Su estructura es:

            {
                "ruta": Path(...),
                "nombre": "factura.pdf",
                "cantidad_paginas": 1,
                "paginas_con_texto": 1,
                "paginas_sin_texto": 0,
                "contiene_texto": True,
                "paginas": [...],
                "texto_completo": "..."
            }

    Importante
    ----------
    La función devuelve información estructurada.

    No imprime el resultado directamente porque la salida
    visual corresponde a console_output.py y main.py.
    """

    ruta_pdf = validar_ruta_pdf(
        ruta_pdf
    )

    paginas = extraer_paginas_pdf(
        ruta_pdf
    )

    cantidad_paginas = len(
        paginas
    )

    paginas_con_texto = sum(
        1
        for pagina in paginas
        if pagina["texto"]
    )

    paginas_sin_texto = (
        cantidad_paginas
        -
        paginas_con_texto
    )

    texto_completo = unir_texto_paginas(
        paginas
    )

    resultado = {
        "ruta": ruta_pdf,
        "nombre": ruta_pdf.name,
        "cantidad_paginas": cantidad_paginas,
        "paginas_con_texto": paginas_con_texto,
        "paginas_sin_texto": paginas_sin_texto,
        "contiene_texto": bool(texto_completo),
        "paginas": paginas,
        "texto_completo": texto_completo
    }

    return resultado

# ==========================================================
# FIN DE LA FUNCIÓN leer_pdf()
# ==========================================================


# ==========================================================
# FIN DEL ARCHIVO
# ==========================================================