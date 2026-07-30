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

La versión actual del proyecto no se encuentra escrita
directamente en este archivo.

Cada vez que el programa se ejecuta, main.py importa:

    version.py

y obtiene el valor de:

    version.PROJECT_VERSION

Esto permite actualizar la versión modificando solamente
el archivo version.py.

La salida visual de la consola se encuentra centralizada
parcialmente dentro del módulo:

    console_output.py

Actualmente, el programa realiza los siguientes pasos:

1. Muestra la información general del proyecto.
2. Muestra la configuración utilizada.
3. Se conecta con Gmail.
4. Busca todos los correos de la cuenta.
5. Selecciona una cantidad limitada de correos recientes.
6. Recorre los correos seleccionados.
7. Lee cada correo completo.
8. Extrae sus encabezados principales.
9. Detecta sus archivos adjuntos.
10. Determina una carpeta según el remitente y la fecha.
11. Filtra únicamente los archivos PDF.
12. Evita volver a guardar archivos que ya existan.
13. Guarda los PDF nuevos.
14. Conserva la ruta de los PDF que ya existían.
15. Lee el contenido interno de todos los PDF encontrados.
16. Detecta documentos sin texto extraíble.
17. Muestra una vista previa del texto encontrado.
18. Muestra un resumen final.
19. Cierra correctamente la conexión con Gmail.

La estructura de carpetas utilizada es:

    Facturas
        └── Remitente
            └── Año
                └── Número - Mes
                    └── factura.pdf

Autor
-----
Diego (desarrollador del proyecto)
ChatGPT (mentor técnico)

==========================================================
"""


# ==========================================================
# INICIO DEL BLOQUE DE IMPORTACIONES
# ==========================================================

import config
import console_output
import file_manager
import gmail_client
import invoice_organizer
import pdf_reader
import version

# ==========================================================
# FIN DEL BLOQUE DE IMPORTACIONES
# ==========================================================


# ==========================================================
# INICIO DEL BLOQUE DE CONSTANTES
# ==========================================================

# ----------------------------------------------------------
# Esta constante determina cuántos caracteres del texto de
# cada PDF se mostrarán en la consola.
#
# El documento se lee completo, pero mostrar todo el texto de
# muchas facturas produciría una salida demasiado extensa.
#
# Más adelante este valor podría trasladarse a config.py.
# ----------------------------------------------------------

LIMITE_VISTA_PREVIA_PDF = 500

# ==========================================================
# FIN DEL BLOQUE DE CONSTANTES
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN mostrar_informacion_proyecto()
# ==========================================================

def mostrar_informacion_proyecto():
    """
    Mostrar la información general del proyecto.

    Actualmente muestra:

    - Nombre del proyecto.
    - Versión obtenida desde version.py.
    - Autor.
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

# ==========================================================
# FIN DE LA FUNCIÓN mostrar_informacion_proyecto()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN mostrar_configuracion()
# ==========================================================

def mostrar_configuracion():
    """
    Mostrar los valores públicos de configuración utilizados
    por el programa.

    La contraseña de aplicación nunca debe mostrarse.
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
# FIN DE LA FUNCIÓN mostrar_configuracion()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN mostrar_resultado_busqueda()
# ==========================================================

def mostrar_resultado_busqueda(identificadores_correos):
    """
    Mostrar cuántos correos fueron encontrados.

    Parámetros
    ----------
    identificadores_correos:

        Lista de identificadores IMAP devuelta por:

            gmail_client.buscar_todos_los_correos()
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

# ==========================================================
# FIN DE LA FUNCIÓN mostrar_resultado_busqueda()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN seleccionar_correos_recientes()
# ==========================================================

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

        Cantidad máxima de correos que deseamos procesar.

    Retorna
    -------
    list

        Lista con los identificadores seleccionados.

        Los correos se devuelven ordenados desde el más
        reciente hasta el más antiguo.

    Ejemplo
    -------
    Si recibimos:

        [b'1', b'2', b'3', b'4', b'5']

    y el límite es 3, devuelve:

        [b'5', b'4', b'3']
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

# ==========================================================
# FIN DE LA FUNCIÓN seleccionar_correos_recientes()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN mostrar_correos_seleccionados()
# ==========================================================

def mostrar_correos_seleccionados(cantidad_seleccionada):
    """
    Mostrar la cantidad de correos que serán procesados.

    Parámetros
    ----------
    cantidad_seleccionada:

        Cantidad de correos elegidos según el límite
        configurado.
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

# ==========================================================
# FIN DE LA FUNCIÓN mostrar_correos_seleccionados()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN mostrar_inicio_correo()
# ==========================================================

def mostrar_inicio_correo(
    numero_correo,
    cantidad_correos,
    id_correo
):
    """
    Mostrar el comienzo del procesamiento de un correo.

    Parámetros
    ----------
    numero_correo:

        Posición actual dentro del recorrido.

    cantidad_correos:

        Cantidad total de correos seleccionados.

    id_correo:

        Identificador IMAP del correo actual.
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
# FIN DE LA FUNCIÓN mostrar_inicio_correo()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN mostrar_datos_correo()
# ==========================================================

def mostrar_datos_correo(datos_correo):
    """
    Mostrar los encabezados principales de un correo.

    Parámetros
    ----------
    datos_correo:

        Diccionario devuelto por:

            gmail_client.obtener_datos_correo()
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

# ==========================================================
# FIN DE LA FUNCIÓN mostrar_datos_correo()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN mostrar_adjuntos()
# ==========================================================

def mostrar_adjuntos(adjuntos):
    """
    Mostrar información sobre los archivos adjuntos
    detectados dentro de un correo.
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

# ==========================================================
# FIN DE LA FUNCIÓN mostrar_adjuntos()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN mostrar_carpeta_asignada()
# ==========================================================

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
# FIN DE LA FUNCIÓN mostrar_carpeta_asignada()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN mostrar_resultados_archivos_pdf()
# ==========================================================

def mostrar_resultados_archivos_pdf(resultados_archivos):
    """
    Mostrar el resultado del guardado de todos los PDF
    encontrados dentro del correo actual.

    Parámetros
    ----------
    resultados_archivos:

        Lista devuelta por:

            file_manager.procesar_adjuntos_pdf()

        Cada elemento informa si el archivo fue guardado o si
        ya existía previamente.
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
# FIN DE LA FUNCIÓN mostrar_resultados_archivos_pdf()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN crear_vista_previa_texto()
# ==========================================================

def crear_vista_previa_texto(
    texto,
    limite=LIMITE_VISTA_PREVIA_PDF
):
    """
    Crear una versión abreviada del texto de un PDF.

    Parámetros
    ----------
    texto:

        Texto completo extraído del documento.

    limite:

        Cantidad máxima de caracteres que se mostrarán.

    Retorna
    -------
    str

        Texto abreviado.

        Si el contenido supera el límite, se agregan puntos
        suspensivos al final.

    Importante
    ----------
    El texto completo continúa disponible dentro del
    resultado devuelto por pdf_reader.leer_pdf().

    Esta función solamente limita lo que aparece en pantalla.
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

# ==========================================================
# FIN DE LA FUNCIÓN crear_vista_previa_texto()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN leer_archivos_pdf()
# ==========================================================

def leer_archivos_pdf(resultados_archivos):
    """
    Leer todos los archivos PDF detectados en un correo.

    Parámetros
    ----------
    resultados_archivos:

        Lista devuelta por:

            file_manager.procesar_adjuntos_pdf()

    Retorna
    -------
    list

        Lista de diccionarios.

        Para una lectura correcta:

            {
                "nombre": "factura.pdf",
                "ruta": Path(...),
                "lectura_correcta": True,
                "contiene_texto": True,
                "resultado_lectura": {...},
                "error": None
            }

        Para una lectura con error:

            {
                "nombre": "factura.pdf",
                "ruta": Path(...),
                "lectura_correcta": False,
                "contiene_texto": False,
                "resultado_lectura": None,
                "error": excepción
            }

    Comportamiento ante errores
    ---------------------------
    Si un PDF individual no puede leerse, el error se guarda
    dentro del resultado.

    La función continúa procesando los demás documentos.
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

# ==========================================================
# FIN DE LA FUNCIÓN leer_archivos_pdf()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN mostrar_resultados_lectura_pdf()
# ==========================================================

def mostrar_resultados_lectura_pdf(resultados_lectura):
    """
    Mostrar el resultado de la lectura de los archivos PDF.

    El texto se muestra mediante una vista previa para evitar
    llenar la consola con documentos completos.
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
# FIN DE LA FUNCIÓN mostrar_resultados_lectura_pdf()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN procesar_correo()
# ==========================================================

def procesar_correo(conexion, id_correo):
    """
    Leer y procesar un único correo.

    Retorna
    -------
    dict

        Diccionario con:

        - Los PDF encontrados.
        - Los resultados de lectura de esos PDF.

        Su estructura es:

            {
                "resultados_archivos": [...],
                "resultados_lectura": [...]
            }
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

    # ------------------------------------------------------
    # Esta nueva función devuelve información sobre todos los
    # PDF encontrados.
    #
    # Incluye tanto:
    #
    # - Los PDF nuevos.
    # - Los PDF que ya existían.
    # ------------------------------------------------------

    resultados_archivos = (
        file_manager.procesar_adjuntos_pdf(
            adjuntos,
            carpeta_factura
        )
    )

    mostrar_resultados_archivos_pdf(
        resultados_archivos
    )

    # ------------------------------------------------------
    # Una vez que conocemos la ruta de cada PDF, intentamos
    # leer su contenido.
    #
    # Los archivos existentes también serán leídos.
    # ------------------------------------------------------

    resultados_lectura = leer_archivos_pdf(
        resultados_archivos
    )

    mostrar_resultados_lectura_pdf(
        resultados_lectura
    )

    return {
        "resultados_archivos": resultados_archivos,
        "resultados_lectura": resultados_lectura
    }

# ==========================================================
# FIN DE LA FUNCIÓN procesar_correo()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN mostrar_error_correo()
# ==========================================================

def mostrar_error_correo(id_correo, error_correo):
    """
    Mostrar información sobre un error producido al procesar
    un correo específico.
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
# FIN DE LA FUNCIÓN mostrar_error_correo()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN mostrar_resumen_final()
# ==========================================================

def mostrar_resumen_final(
    cantidad_seleccionada,
    cantidad_procesada,
    cantidad_errores,
    todos_los_resultados_archivos,
    todos_los_resultados_lectura
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
        cantidad_errores_lectura,
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
# FIN DE LA FUNCIÓN mostrar_resumen_final()
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN main()
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
            todos_los_resultados_lectura
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
# FIN DE LA FUNCIÓN main()
# ==========================================================


# ==========================================================
# PUNTO DE ENTRADA DEL PROGRAMA
# ==========================================================

if __name__ == "__main__":

    main()


# ==========================================================
# FIN DEL ARCHIVO
# ==========================================================