"""
==========================================================
PROYECTO
==========================================================

Proyecto Facturas

Archivo
-------
main.py

Descripción
-----------
Este archivo funciona como punto de entrada principal del
programa.

Su responsabilidad consiste en coordinar las funciones
definidas en los demás módulos.

Actualmente, el programa:

1. Muestra la información del proyecto.
2. Muestra la configuración.
3. Se conecta con Gmail.
4. Busca y selecciona correos recientes.
5. Procesa los archivos adjuntos PDF.
6. Guarda los PDF nuevos.
7. Reconoce los PDF que ya existían.
8. Lee el contenido interno de los PDF.
9. Detecta los documentos sin texto extraíble.
10. Muestra una vista previa del texto.
11. Detecta el proveedor de cada factura.
12. Muestra un resumen final.
13. Cierra correctamente la conexión con Gmail.

Autor
-----
Diego (desarrollador del proyecto)
ChatGPT (mentor técnico)

==========================================================
"""


# ==========================================================
# IMPORTACIONES
# ==========================================================

import config
import console_output
import file_manager
import gmail_client
import invoice_organizer
import pdf_reader
import supplier_detector
import version


# ==========================================================
# CONSTANTES
# ==========================================================

# Cantidad máxima de caracteres del texto de cada PDF que
# serán mostrados en la consola.
#
# El PDF se lee completo. Esta constante solamente limita
# la vista previa que se imprime en pantalla.

LIMITE_VISTA_PREVIA_PDF = 500


# ==========================================================
# INFORMACIÓN GENERAL
# ==========================================================

def mostrar_informacion_proyecto():
    """
    Mostrar la información general del proyecto.
    """

    console_output.linea_en_blanco()

    console_output.mostrar_titulo(
        "INFORMACIÓN DEL PROYECTO"
    )

    console_output.mostrar_etiqueta_valor(
        "Proyecto:",
        config.PROJECT_NAME
    )

    console_output.mostrar_etiqueta_valor(
        "Versión:",
        version.PROJECT_VERSION
    )

    console_output.mostrar_etiqueta_valor(
        "Autor:",
        config.PROJECT_AUTHOR,
        espacio_despues=False
    )

    print(console_output.SEPARADOR_PRINCIPAL)


def mostrar_configuracion():
    """
    Mostrar los valores públicos de configuración.

    La contraseña de aplicación de Gmail nunca debe
    mostrarse en la consola.
    """

    console_output.linea_en_blanco()

    console_output.mostrar_titulo(
        "CONFIGURACIÓN"
    )

    console_output.mostrar_etiqueta_valor(
        "Cuenta de Gmail:",
        config.EMAIL
    )

    console_output.mostrar_etiqueta_valor(
        "Carpeta de destino:",
        config.SAVE_FOLDER
    )

    console_output.mostrar_etiqueta_valor(
        "Límite de correos por ejecución:",
        config.EMAIL_PROCESSING_LIMIT,
        espacio_despues=False
    )

    print(console_output.SEPARADOR_PRINCIPAL)


# ==========================================================
# SELECCIÓN DE CORREOS
# ==========================================================

def mostrar_resultado_busqueda(identificadores_correos):
    """
    Mostrar cuántos correos fueron encontrados.
    """

    cantidad_correos = len(
        identificadores_correos
    )

    console_output.linea_en_blanco()

    console_output.mostrar_titulo(
        "RESULTADO DE LA BÚSQUEDA"
    )

    console_output.mostrar_etiqueta_valor(
        "Cantidad total de correos encontrados:",
        cantidad_correos,
        espacio_despues=False
    )

    print(console_output.SEPARADOR_PRINCIPAL)


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


def mostrar_correos_seleccionados(cantidad_seleccionada):
    """
    Mostrar la cantidad de correos que serán procesados.
    """

    console_output.linea_en_blanco()

    console_output.mostrar_titulo(
        "CORREOS SELECCIONADOS"
    )

    console_output.mostrar_etiqueta_valor(
        "Cantidad de correos que serán procesados:",
        cantidad_seleccionada,
        espacio_despues=False
    )

    print(console_output.SEPARADOR_PRINCIPAL)


def mostrar_inicio_correo(
    numero_correo,
    cantidad_correos,
    id_correo
):
    """
    Mostrar el comienzo del procesamiento de un correo.
    """

    console_output.linea_en_blanco()
    console_output.linea_en_blanco()

    console_output.mostrar_inicio_procesamiento(
        numero_correo,
        cantidad_correos
    )

    console_output.mostrar_etiqueta_valor(
        "ID del correo:",
        id_correo,
        espacio_despues=False
    )


# ==========================================================
# INFORMACIÓN DEL CORREO
# ==========================================================

def mostrar_datos_correo(datos_correo):
    """
    Mostrar los encabezados principales de un correo.
    """

    console_output.linea_en_blanco()

    console_output.mostrar_titulo(
        "DATOS PRINCIPALES DEL CORREO"
    )

    console_output.mostrar_etiqueta_valor(
        "Asunto:",
        datos_correo["Subject"]
    )

    console_output.mostrar_etiqueta_valor(
        "Remitente:",
        datos_correo["From"]
    )

    console_output.mostrar_etiqueta_valor(
        "Destinatario:",
        datos_correo["To"]
    )

    console_output.mostrar_etiqueta_valor(
        "Fecha:",
        datos_correo["Date"],
        espacio_despues=False
    )

    print(console_output.SEPARADOR_PRINCIPAL)


def mostrar_adjuntos(adjuntos):
    """
    Mostrar los archivos adjuntos detectados en un correo.
    """

    cantidad_adjuntos = len(
        adjuntos
    )

    console_output.linea_en_blanco()

    console_output.mostrar_titulo(
        "ARCHIVOS ADJUNTOS"
    )

    console_output.mostrar_etiqueta_valor(
        "Cantidad de adjuntos encontrados:",
        cantidad_adjuntos,
        espacio_despues=False
    )

    if not adjuntos:

        console_output.linea_en_blanco()

        console_output.mostrar_mensaje(
            "El correo no contiene archivos adjuntos."
        )

        print(console_output.SEPARADOR_PRINCIPAL)

        return

    for numero_adjunto, adjunto in enumerate(
        adjuntos,
        start=1
    ):

        console_output.linea_en_blanco()

        console_output.mostrar_subtitulo(
            f"Adjunto número {numero_adjunto}"
        )

        console_output.mostrar_etiqueta_valor(
            "Nombre:",
            adjunto["nombre"]
        )

        console_output.mostrar_etiqueta_valor(
            "Tipo de contenido:",
            adjunto["tipo_contenido"],
            espacio_despues=False
        )

    console_output.linea_en_blanco()

    print(console_output.SEPARADOR_PRINCIPAL)


def mostrar_carpeta_asignada(carpeta_factura):
    """
    Mostrar la carpeta asignada al correo actual.
    """

    console_output.linea_en_blanco()

    console_output.mostrar_titulo(
        "CARPETA ASIGNADA"
    )

    console_output.mostrar_etiqueta_valor(
        "Los archivos PDF de este correo se guardarán en:",
        carpeta_factura,
        espacio_despues=False
    )

    print(console_output.SEPARADOR_PRINCIPAL)


# ==========================================================
# PROCESAMIENTO DE ARCHIVOS PDF
# ==========================================================

def mostrar_resultados_archivos_pdf(resultados_archivos):
    """
    Mostrar el resultado del procesamiento de los PDF.

    La función informa:

    - Cuántos PDF fueron encontrados.
    - Cuántos fueron guardados.
    - Cuántos ya existían.
    - La ruta de cada documento.
    """

    cantidad_pdf = len(
        resultados_archivos
    )

    cantidad_nuevos = sum(
        1
        for resultado in resultados_archivos
        if resultado["fue_guardado"]
    )

    cantidad_existentes = sum(
        1
        for resultado in resultados_archivos
        if resultado["ya_existia"]
    )

    console_output.linea_en_blanco()

    console_output.mostrar_titulo(
        "RESULTADO DE LOS ARCHIVOS PDF"
    )

    console_output.mostrar_etiqueta_valor(
        "Cantidad de archivos PDF encontrados:",
        cantidad_pdf
    )

    console_output.mostrar_etiqueta_valor(
        "Archivos PDF nuevos guardados:",
        cantidad_nuevos
    )

    console_output.mostrar_etiqueta_valor(
        "Archivos PDF que ya existían:",
        cantidad_existentes,
        espacio_despues=False
    )

    if not resultados_archivos:

        console_output.linea_en_blanco()

        console_output.mostrar_mensaje(
            "El correo no contiene archivos PDF."
        )

        print(console_output.SEPARADOR_PRINCIPAL)

        return

    for numero_archivo, resultado in enumerate(
        resultados_archivos,
        start=1
    ):

        console_output.linea_en_blanco()

        console_output.mostrar_subtitulo(
            f"Archivo PDF número {numero_archivo}"
        )

        console_output.mostrar_etiqueta_valor(
            "Nombre:",
            resultado["nombre"]
        )

        console_output.mostrar_etiqueta_valor(
            "Ruta:",
            resultado["ruta"]
        )

        if resultado["fue_guardado"]:

            estado_archivo = (
                "Archivo nuevo guardado correctamente."
            )

        else:

            estado_archivo = (
                "El archivo ya existía y no fue guardado "
                "nuevamente."
            )

        console_output.mostrar_etiqueta_valor(
            "Estado:",
            estado_archivo,
            espacio_despues=False
        )

    console_output.linea_en_blanco()

    print(console_output.SEPARADOR_PRINCIPAL)


# ==========================================================
# LECTURA DE ARCHIVOS PDF
# ==========================================================

def crear_vista_previa_texto(
    texto,
    limite=LIMITE_VISTA_PREVIA_PDF
):
    """
    Crear una versión abreviada del texto de un PDF.

    El texto completo continúa disponible en el resultado de
    pdf_reader.leer_pdf(). Esta función solamente limita el
    contenido mostrado en la consola.
    """

    if not texto:

        return ""

    texto = str(
        texto
    ).strip()

    if len(texto) <= limite:

        return texto

    vista_previa = texto[
        :limite
    ].rstrip()

    vista_previa += "\n[...]"

    return vista_previa


def leer_archivos_pdf(resultados_archivos):
    """
    Leer todos los archivos PDF detectados en un correo.

    Si un PDF individual produce un error, el error se guarda
    dentro de su resultado y el programa continúa con los
    demás documentos.
    """

    resultados_lectura = []

    for resultado_archivo in resultados_archivos:

        ruta_pdf = resultado_archivo["ruta"]

        try:

            resultado_lectura = pdf_reader.leer_pdf(
                ruta_pdf
            )

            informacion = {
                "nombre": resultado_archivo["nombre"],
                "ruta": ruta_pdf,
                "lectura_correcta": True,
                "contiene_texto": (
                    resultado_lectura["contiene_texto"]
                ),
                "resultado_lectura": resultado_lectura,
                "error": None
            }

        except Exception as error:

            informacion = {
                "nombre": resultado_archivo["nombre"],
                "ruta": ruta_pdf,
                "lectura_correcta": False,
                "contiene_texto": False,
                "resultado_lectura": None,
                "error": error
            }

        resultados_lectura.append(
            informacion
        )

    return resultados_lectura


def mostrar_resultados_lectura_pdf(resultados_lectura):
    """
    Mostrar el resultado de la lectura de los archivos PDF.
    """

    cantidad_pdf = len(
        resultados_lectura
    )

    lecturas_correctas = sum(
        1
        for resultado in resultados_lectura
        if resultado["lectura_correcta"]
    )

    lecturas_con_error = sum(
        1
        for resultado in resultados_lectura
        if not resultado["lectura_correcta"]
    )

    pdf_con_texto = sum(
        1
        for resultado in resultados_lectura
        if (
            resultado["lectura_correcta"]
            and
            resultado["contiene_texto"]
        )
    )

    pdf_sin_texto = sum(
        1
        for resultado in resultados_lectura
        if (
            resultado["lectura_correcta"]
            and
            not resultado["contiene_texto"]
        )
    )

    console_output.linea_en_blanco()

    console_output.mostrar_titulo(
        "LECTURA DEL CONTENIDO DE LOS PDF"
    )

    console_output.mostrar_etiqueta_valor(
        "Cantidad de PDF enviados a lectura:",
        cantidad_pdf
    )

    console_output.mostrar_etiqueta_valor(
        "PDF leídos correctamente:",
        lecturas_correctas
    )

    console_output.mostrar_etiqueta_valor(
        "PDF con texto extraíble:",
        pdf_con_texto
    )

    console_output.mostrar_etiqueta_valor(
        "PDF sin texto extraíble:",
        pdf_sin_texto
    )

    console_output.mostrar_etiqueta_valor(
        "PDF con errores de lectura:",
        lecturas_con_error,
        espacio_despues=False
    )

    if not resultados_lectura:

        console_output.linea_en_blanco()

        console_output.mostrar_mensaje(
            "No hay archivos PDF para leer."
        )

        print(console_output.SEPARADOR_PRINCIPAL)

        return

    for numero_pdf, resultado in enumerate(
        resultados_lectura,
        start=1
    ):

        console_output.linea_en_blanco()

        console_output.mostrar_subtitulo(
            f"Lectura del PDF número {numero_pdf}"
        )

        console_output.mostrar_etiqueta_valor(
            "Nombre:",
            resultado["nombre"]
        )

        console_output.mostrar_etiqueta_valor(
            "Ruta:",
            resultado["ruta"]
        )

        if not resultado["lectura_correcta"]:

            error = resultado["error"]

            console_output.mostrar_etiqueta_valor(
                "Estado:",
                "No fue posible leer el documento."
            )

            console_output.mostrar_etiqueta_valor(
                "Tipo de error:",
                type(error).__name__
            )

            console_output.mostrar_etiqueta_valor(
                "Descripción:",
                error,
                espacio_despues=False
            )

            continue

        datos_lectura = resultado[
            "resultado_lectura"
        ]

        console_output.mostrar_etiqueta_valor(
            "Estado:",
            "Documento leído correctamente."
        )

        console_output.mostrar_etiqueta_valor(
            "Cantidad de páginas:",
            datos_lectura["cantidad_paginas"]
        )

        console_output.mostrar_etiqueta_valor(
            "Páginas con texto:",
            datos_lectura["paginas_con_texto"]
        )

        console_output.mostrar_etiqueta_valor(
            "Páginas sin texto:",
            datos_lectura["paginas_sin_texto"]
        )

        if not datos_lectura["contiene_texto"]:

            console_output.mostrar_etiqueta_valor(
                "Contenido:",
                (
                    "El documento no contiene texto "
                    "extraíble. Puede tratarse de un PDF "
                    "escaneado."
                ),
                espacio_despues=False
            )

            continue

        vista_previa = crear_vista_previa_texto(
            datos_lectura["texto_completo"]
        )

        console_output.mostrar_etiqueta_valor(
            "Vista previa del texto extraído:",
            vista_previa,
            espacio_despues=False
        )

    console_output.linea_en_blanco()

    print(console_output.SEPARADOR_PRINCIPAL)


# ==========================================================
# DETECCIÓN DE PROVEEDORES
# ==========================================================

def detectar_proveedores_pdf(resultados_lectura):
    """
    Intentar detectar el proveedor de cada PDF leído.

    Parámetros
    ----------
    resultados_lectura:
        Lista devuelta por leer_archivos_pdf().

    Retorna
    -------
    list
        Lista con un resultado de detección por cada PDF.

    Casos posibles
    --------------
    1. El PDF fue leído, contiene texto y la detección pudo
       realizarse.

    2. El PDF fue leído, pero no contiene texto extraíble.

    3. El PDF no pudo leerse.

    4. Se produjo un error específico durante la detección.

    Un error en un documento no detiene el procesamiento de
    los demás PDF.
    """

    resultados_proveedores = []

    for resultado_lectura in resultados_lectura:

        nombre = resultado_lectura["nombre"]
        ruta = resultado_lectura["ruta"]

        # --------------------------------------------------
        # Si el PDF no pudo leerse, tampoco podemos analizar
        # su texto para detectar un proveedor.
        # --------------------------------------------------

        if not resultado_lectura["lectura_correcta"]:

            informacion = {
                "nombre": nombre,
                "ruta": ruta,
                "deteccion_realizada": False,
                "motivo_no_realizada": (
                    "El PDF no pudo ser leído."
                ),
                "resultado_proveedor": None,
                "error": None
            }

            resultados_proveedores.append(
                informacion
            )

            continue

        # --------------------------------------------------
        # Si el documento fue leído pero no tiene texto,
        # supplier_detector no dispone de contenido sobre el
        # cual realizar la búsqueda.
        # --------------------------------------------------

        if not resultado_lectura["contiene_texto"]:

            informacion = {
                "nombre": nombre,
                "ruta": ruta,
                "deteccion_realizada": False,
                "motivo_no_realizada": (
                    "El PDF no contiene texto extraíble."
                ),
                "resultado_proveedor": None,
                "error": None
            }

            resultados_proveedores.append(
                informacion
            )

            continue

        try:

            datos_lectura = resultado_lectura[
                "resultado_lectura"
            ]

            texto_completo = datos_lectura[
                "texto_completo"
            ]

            resultado_proveedor = (
                supplier_detector.detectar_proveedor(
                    texto_completo
                )
            )

            informacion = {
                "nombre": nombre,
                "ruta": ruta,
                "deteccion_realizada": True,
                "motivo_no_realizada": None,
                "resultado_proveedor": resultado_proveedor,
                "error": None
            }

        except Exception as error:

            informacion = {
                "nombre": nombre,
                "ruta": ruta,
                "deteccion_realizada": False,
                "motivo_no_realizada": (
                    "Se produjo un error durante la "
                    "detección del proveedor."
                ),
                "resultado_proveedor": None,
                "error": error
            }

        resultados_proveedores.append(
            informacion
        )

    return resultados_proveedores


def mostrar_resultados_proveedores(
    resultados_proveedores
):
    """
    Mostrar los resultados de la detección de proveedores.
    """

    cantidad_documentos = len(
        resultados_proveedores
    )

    cantidad_detecciones_realizadas = sum(
        1
        for resultado in resultados_proveedores
        if resultado["deteccion_realizada"]
    )

    cantidad_proveedores_detectados = sum(
        1
        for resultado in resultados_proveedores
        if (
            resultado["deteccion_realizada"]
            and
            resultado["resultado_proveedor"][
                "proveedor_detectado"
            ]
        )
    )

    cantidad_proveedores_no_detectados = sum(
        1
        for resultado in resultados_proveedores
        if (
            resultado["deteccion_realizada"]
            and
            not resultado["resultado_proveedor"][
                "proveedor_detectado"
            ]
        )
    )

    cantidad_no_analizados = sum(
        1
        for resultado in resultados_proveedores
        if not resultado["deteccion_realizada"]
    )

    cantidad_errores = sum(
        1
        for resultado in resultados_proveedores
        if resultado["error"] is not None
    )

    console_output.linea_en_blanco()

    console_output.mostrar_titulo(
        "DETECCIÓN DE PROVEEDORES"
    )

    console_output.mostrar_etiqueta_valor(
        "Cantidad de PDF recibidos:",
        cantidad_documentos
    )

    console_output.mostrar_etiqueta_valor(
        "Detecciones realizadas:",
        cantidad_detecciones_realizadas
    )

    console_output.mostrar_etiqueta_valor(
        "Proveedores detectados:",
        cantidad_proveedores_detectados
    )

    console_output.mostrar_etiqueta_valor(
        "Proveedores no reconocidos:",
        cantidad_proveedores_no_detectados
    )

    console_output.mostrar_etiqueta_valor(
        "Documentos no analizados:",
        cantidad_no_analizados
    )

    console_output.mostrar_etiqueta_valor(
        "Errores de detección:",
        cantidad_errores,
        espacio_despues=False
    )

    if not resultados_proveedores:

        console_output.linea_en_blanco()

        console_output.mostrar_mensaje(
            "No hay archivos PDF para analizar."
        )

        print(console_output.SEPARADOR_PRINCIPAL)

        return

    for numero_pdf, resultado in enumerate(
        resultados_proveedores,
        start=1
    ):

        console_output.linea_en_blanco()

        console_output.mostrar_subtitulo(
            f"Proveedor del PDF número {numero_pdf}"
        )

        console_output.mostrar_etiqueta_valor(
            "Nombre del archivo:",
            resultado["nombre"]
        )

        console_output.mostrar_etiqueta_valor(
            "Ruta:",
            resultado["ruta"]
        )

        if not resultado["deteccion_realizada"]:

            console_output.mostrar_etiqueta_valor(
                "Estado:",
                "La detección no pudo realizarse."
            )

            console_output.mostrar_etiqueta_valor(
                "Motivo:",
                resultado["motivo_no_realizada"]
            )

            if resultado["error"] is not None:

                error = resultado["error"]

                console_output.mostrar_etiqueta_valor(
                    "Tipo de error:",
                    type(error).__name__
                )

                console_output.mostrar_etiqueta_valor(
                    "Descripción:",
                    error,
                    espacio_despues=False
                )

            else:

                console_output.mostrar_etiqueta_valor(
                    "Error:",
                    "No se produjo un error técnico.",
                    espacio_despues=False
                )

            continue

        resultado_proveedor = resultado[
            "resultado_proveedor"
        ]

        if not resultado_proveedor[
            "proveedor_detectado"
        ]:

            console_output.mostrar_etiqueta_valor(
                "Estado:",
                "Proveedor no reconocido."
            )

            console_output.mostrar_etiqueta_valor(
                "Método de detección:",
                resultado_proveedor[
                    "metodo_deteccion"
                ]
            )

            console_output.mostrar_etiqueta_valor(
                "Nivel de confianza:",
                resultado_proveedor[
                    "nivel_confianza"
                ]
            )

            console_output.mostrar_etiqueta_valor(
                "Puntaje:",
                resultado_proveedor["puntaje"],
                espacio_despues=False
            )

            continue

        console_output.mostrar_etiqueta_valor(
            "Estado:",
            "Proveedor detectado correctamente."
        )

        console_output.mostrar_etiqueta_valor(
            "Identificador interno:",
            resultado_proveedor["identificador"]
        )

        console_output.mostrar_etiqueta_valor(
            "Nombre del proveedor:",
            resultado_proveedor["nombre_proveedor"]
        )

        console_output.mostrar_etiqueta_valor(
            "Razón social encontrada:",
            resultado_proveedor[
                "razon_social_encontrada"
            ]
        )

        console_output.mostrar_etiqueta_valor(
            "CUIT encontrado:",
            resultado_proveedor["cuit_encontrado"]
        )

        console_output.mostrar_etiqueta_valor(
            "Método de detección:",
            resultado_proveedor[
                "metodo_deteccion"
            ]
        )

        console_output.mostrar_etiqueta_valor(
            "Nivel de confianza:",
            resultado_proveedor[
                "nivel_confianza"
            ]
        )

        console_output.mostrar_etiqueta_valor(
            "Puntaje:",
            resultado_proveedor["puntaje"],
            espacio_despues=False
        )

    console_output.linea_en_blanco()

    print(console_output.SEPARADOR_PRINCIPAL)


# ==========================================================
# PROCESAMIENTO DE UN CORREO
# ==========================================================

def procesar_correo(conexion, id_correo):
    """
    Leer y procesar un único correo.

    Retorna
    -------
    dict
        Diccionario con:

        - Los resultados del procesamiento de archivos.
        - Los resultados de lectura de los PDF.
        - Los resultados de detección de proveedores.
    """

    mensaje = gmail_client.leer_correo(
        conexion,
        id_correo
    )

    datos_correo = gmail_client.obtener_datos_correo(
        mensaje
    )

    mostrar_datos_correo(
        datos_correo
    )

    adjuntos = gmail_client.obtener_adjuntos(
        mensaje
    )

    mostrar_adjuntos(
        adjuntos
    )

    carpeta_factura = (
        invoice_organizer.construir_carpeta_factura(
            config.SAVE_FOLDER,
            datos_correo
        )
    )

    mostrar_carpeta_asignada(
        carpeta_factura
    )

    # Procesar tanto los PDF nuevos como aquellos que ya
    # existían previamente.

    resultados_archivos = (
        file_manager.procesar_adjuntos_pdf(
            adjuntos,
            carpeta_factura
        )
    )

    mostrar_resultados_archivos_pdf(
        resultados_archivos
    )

    # Leer el contenido de todos los PDF encontrados.

    resultados_lectura = leer_archivos_pdf(
        resultados_archivos
    )

    mostrar_resultados_lectura_pdf(
        resultados_lectura
    )

    # Detectar el proveedor utilizando el texto extraído de
    # cada documento.

    resultados_proveedores = detectar_proveedores_pdf(
        resultados_lectura
    )

    mostrar_resultados_proveedores(
        resultados_proveedores
    )

    return {
        "resultados_archivos": resultados_archivos,
        "resultados_lectura": resultados_lectura,
        "resultados_proveedores": resultados_proveedores
    }


# ==========================================================
# ERRORES DE CORREOS
# ==========================================================

def mostrar_error_correo(id_correo, error_correo):
    """
    Mostrar un error producido al procesar un correo.
    """

    console_output.linea_en_blanco()

    console_output.mostrar_titulo(
        "ERROR AL PROCESAR EL CORREO"
    )

    console_output.mostrar_etiqueta_valor(
        "ID del correo:",
        id_correo
    )

    console_output.mostrar_etiqueta_valor(
        "Tipo de error:",
        type(error_correo).__name__
    )

    console_output.mostrar_etiqueta_valor(
        "Descripción:",
        error_correo
    )

    console_output.mostrar_mensaje(
        "El programa continuará con el siguiente correo."
    )

    print(console_output.SEPARADOR_PRINCIPAL)


# ==========================================================
# RESUMEN FINAL
# ==========================================================

def mostrar_resumen_final(
    cantidad_seleccionada,
    cantidad_procesada,
    cantidad_errores,
    todos_los_resultados_archivos,
    todos_los_resultados_lectura,
    todos_los_resultados_proveedores
):
    """
    Mostrar un resumen general al finalizar la ejecución.
    """

    cantidad_pdf_encontrados = len(
        todos_los_resultados_archivos
    )

    cantidad_pdf_nuevos = sum(
        1
        for resultado in todos_los_resultados_archivos
        if resultado["fue_guardado"]
    )

    cantidad_pdf_existentes = sum(
        1
        for resultado in todos_los_resultados_archivos
        if resultado["ya_existia"]
    )

    cantidad_lecturas_correctas = sum(
        1
        for resultado in todos_los_resultados_lectura
        if resultado["lectura_correcta"]
    )

    cantidad_pdf_con_texto = sum(
        1
        for resultado in todos_los_resultados_lectura
        if (
            resultado["lectura_correcta"]
            and
            resultado["contiene_texto"]
        )
    )

    cantidad_pdf_sin_texto = sum(
        1
        for resultado in todos_los_resultados_lectura
        if (
            resultado["lectura_correcta"]
            and
            not resultado["contiene_texto"]
        )
    )

    cantidad_errores_lectura = sum(
        1
        for resultado in todos_los_resultados_lectura
        if not resultado["lectura_correcta"]
    )

    cantidad_detecciones_realizadas = sum(
        1
        for resultado in todos_los_resultados_proveedores
        if resultado["deteccion_realizada"]
    )

    cantidad_proveedores_detectados = sum(
        1
        for resultado in todos_los_resultados_proveedores
        if (
            resultado["deteccion_realizada"]
            and
            resultado["resultado_proveedor"][
                "proveedor_detectado"
            ]
        )
    )

    cantidad_proveedores_no_detectados = sum(
        1
        for resultado in todos_los_resultados_proveedores
        if (
            resultado["deteccion_realizada"]
            and
            not resultado["resultado_proveedor"][
                "proveedor_detectado"
            ]
        )
    )

    cantidad_detecciones_no_realizadas = sum(
        1
        for resultado in todos_los_resultados_proveedores
        if not resultado["deteccion_realizada"]
    )

    cantidad_errores_deteccion = sum(
        1
        for resultado in todos_los_resultados_proveedores
        if resultado["error"] is not None
    )

    console_output.linea_en_blanco()
    console_output.linea_en_blanco()

    console_output.mostrar_titulo(
        "RESUMEN FINAL"
    )

    console_output.mostrar_etiqueta_valor(
        "Correos seleccionados:",
        cantidad_seleccionada
    )

    console_output.mostrar_etiqueta_valor(
        "Correos procesados correctamente:",
        cantidad_procesada
    )

    console_output.mostrar_etiqueta_valor(
        "Correos con errores:",
        cantidad_errores
    )

    console_output.mostrar_etiqueta_valor(
        "Total de archivos PDF encontrados:",
        cantidad_pdf_encontrados
    )

    console_output.mostrar_etiqueta_valor(
        "Archivos PDF nuevos guardados:",
        cantidad_pdf_nuevos
    )

    console_output.mostrar_etiqueta_valor(
        "Archivos PDF que ya existían:",
        cantidad_pdf_existentes
    )

    console_output.mostrar_etiqueta_valor(
        "PDF leídos correctamente:",
        cantidad_lecturas_correctas
    )

    console_output.mostrar_etiqueta_valor(
        "PDF con texto extraíble:",
        cantidad_pdf_con_texto
    )

    console_output.mostrar_etiqueta_valor(
        "PDF sin texto extraíble:",
        cantidad_pdf_sin_texto
    )

    console_output.mostrar_etiqueta_valor(
        "PDF con errores de lectura:",
        cantidad_errores_lectura
    )

    console_output.mostrar_etiqueta_valor(
        "Detecciones de proveedor realizadas:",
        cantidad_detecciones_realizadas
    )

    console_output.mostrar_etiqueta_valor(
        "Proveedores detectados:",
        cantidad_proveedores_detectados
    )

    console_output.mostrar_etiqueta_valor(
        "Proveedores no reconocidos:",
        cantidad_proveedores_no_detectados
    )

    console_output.mostrar_etiqueta_valor(
        "Detecciones de proveedor no realizadas:",
        cantidad_detecciones_no_realizadas
    )

    console_output.mostrar_etiqueta_valor(
        "Errores durante la detección de proveedores:",
        cantidad_errores_deteccion,
        espacio_despues=False
    )

    archivos_nuevos = [
        resultado["ruta"]
        for resultado in todos_los_resultados_archivos
        if resultado["fue_guardado"]
    ]

    if archivos_nuevos:

        console_output.linea_en_blanco()

        console_output.mostrar_mensaje(
            "Archivos guardados durante esta ejecución:"
        )

        for numero_archivo, ruta_archivo in enumerate(
            archivos_nuevos,
            start=1
        ):

            console_output.linea_en_blanco()

            console_output.mostrar_mensaje(
                f"{numero_archivo}. {ruta_archivo}"
            )

    console_output.linea_en_blanco()

    print(console_output.SEPARADOR_PRINCIPAL)


# ==========================================================
# FUNCIÓN PRINCIPAL
# ==========================================================

def main():
    """
    Coordinar el flujo completo del programa.
    """

    mostrar_informacion_proyecto()

    mostrar_configuracion()

    conexion = None

    try:

        conexion = gmail_client.conectar()

        identificadores_correos = (
            gmail_client.buscar_todos_los_correos(
                conexion
            )
        )

        mostrar_resultado_busqueda(
            identificadores_correos
        )

        if not identificadores_correos:

            console_output.linea_en_blanco()

            console_output.mostrar_mensaje(
                "No se encontraron correos para procesar."
            )

            return

        correos_seleccionados = (
            seleccionar_correos_recientes(
                identificadores_correos,
                config.EMAIL_PROCESSING_LIMIT
            )
        )

        cantidad_seleccionada = len(
            correos_seleccionados
        )

        mostrar_correos_seleccionados(
            cantidad_seleccionada
        )

        cantidad_procesada = 0
        cantidad_errores = 0

        todos_los_resultados_archivos = []
        todos_los_resultados_lectura = []
        todos_los_resultados_proveedores = []

        for numero_correo, id_correo in enumerate(
            correos_seleccionados,
            start=1
        ):

            mostrar_inicio_correo(
                numero_correo,
                cantidad_seleccionada,
                id_correo
            )

            try:

                resultado_correo = procesar_correo(
                    conexion,
                    id_correo
                )

                todos_los_resultados_archivos.extend(
                    resultado_correo[
                        "resultados_archivos"
                    ]
                )

                todos_los_resultados_lectura.extend(
                    resultado_correo[
                        "resultados_lectura"
                    ]
                )

                todos_los_resultados_proveedores.extend(
                    resultado_correo[
                        "resultados_proveedores"
                    ]
                )

                cantidad_procesada += 1

            except Exception as error_correo:

                cantidad_errores += 1

                mostrar_error_correo(
                    id_correo,
                    error_correo
                )

        mostrar_resumen_final(
            cantidad_seleccionada,
            cantidad_procesada,
            cantidad_errores,
            todos_los_resultados_archivos,
            todos_los_resultados_lectura,
            todos_los_resultados_proveedores
        )

    except Exception as error:

        console_output.mostrar_error(
            "SE PRODUJO UN ERROR GENERAL",
            error
        )

    finally:

        if conexion is not None:

            try:

                conexion.logout()

                console_output.linea_en_blanco()

                console_output.mostrar_mensaje(
                    "Conexión cerrada correctamente."
                )

            except Exception as error_cierre:

                console_output.linea_en_blanco()

                console_output.mostrar_mensaje(
                    "No fue posible cerrar la conexión "
                    "de forma normal."
                )

                console_output.mostrar_mensaje(
                    error_cierre
                )


# ==========================================================
# PUNTO DE ENTRADA
# ==========================================================

if __name__ == "__main__":

    main()


# ==========================================================
# FIN DEL ARCHIVO
# ==========================================================