"""Presentación de información en la terminal.

Este módulo contiene únicamente funciones que muestran datos. Separar la
presentación evita mezclar los mensajes de consola con la lógica que descarga,
lee o clasifica facturas.
"""

import config
import console_output
import version

from app.pdf_pipeline import crear_vista_previa_texto

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




def mostrar_resultados_organizacion(resultados):
    """Mostrar si cada PDF llegó a su carpeta final o quedó pendiente."""
    console_output.linea_en_blanco()
    console_output.mostrar_titulo("ORGANIZACIÓN DEFINITIVA")

    if not resultados:
        console_output.mostrar_mensaje("No hay facturas para organizar.")
        print(console_output.SEPARADOR_PRINCIPAL)
        return

    organizadas = sum(resultado["organizada"] for resultado in resultados)
    pendientes = len(resultados) - organizadas
    console_output.mostrar_etiqueta_valor("Facturas organizadas:", organizadas)
    console_output.mostrar_etiqueta_valor(
        "Facturas pendientes de revisión:", pendientes
    )

    for numero, resultado in enumerate(resultados, start=1):
        console_output.mostrar_subtitulo(f"Factura número {numero}")
        if resultado["organizada"]:
            console_output.mostrar_etiqueta_valor(
                "Estado:", "Organizada correctamente."
            )
            console_output.mostrar_etiqueta_valor(
                "Ruta final:", resultado["ruta_final"]
            )
        else:
            console_output.mostrar_etiqueta_valor(
                "Estado:", "Pendiente de revisión."
            )
            console_output.mostrar_etiqueta_valor(
                "Ruta conservada:", resultado["ruta_final"]
            )
            console_output.mostrar_etiqueta_valor(
                "Motivo:", resultado["motivo_pendiente"]
            )

    print(console_output.SEPARADOR_PRINCIPAL)
