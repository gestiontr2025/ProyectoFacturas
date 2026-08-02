"""Procesamiento completo de un correo individual.

Este módulo representa el recorrido de un correo: leerlo, obtener sus adjuntos,
guardar los PDF, extraer su texto y detectar el proveedor. Mantener este flujo
aislado permite que el punto de entrada permanezca breve.
"""

import config
import file_manager
import gmail_client

from app import pdf_pipeline, presentation

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

    presentation.mostrar_datos_correo(
        datos_correo
    )

    adjuntos = gmail_client.obtener_adjuntos(
        mensaje
    )

    presentation.mostrar_adjuntos(
        adjuntos
    )

    # Los adjuntos se descargan primero en una zona temporal. Solo después de
    # leer el PDF y validar sus datos sabemos cuál es su carpeta definitiva.
    carpeta_factura = config.SAVE_FOLDER / "_Pendientes"

    presentation.mostrar_carpeta_asignada(
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

    presentation.mostrar_resultados_archivos_pdf(
        resultados_archivos
    )

    # Leer el contenido de todos los PDF encontrados.

    resultados_lectura = pdf_pipeline.leer_archivos_pdf(
        resultados_archivos
    )

    presentation.mostrar_resultados_lectura_pdf(
        resultados_lectura
    )

    # Detectar el proveedor utilizando el texto extraído de
    # cada documento.

    resultados_proveedores = pdf_pipeline.detectar_proveedores_pdf(
        resultados_lectura
    )

    presentation.mostrar_resultados_proveedores(
        resultados_proveedores
    )

    resultados_organizacion = pdf_pipeline.organizar_facturas_pdf(
        resultados_archivos,
        resultados_lectura,
        resultados_proveedores,
        config.SAVE_FOLDER,
    )

    presentation.mostrar_resultados_organizacion(
        resultados_organizacion
    )

    return {
        "resultados_archivos": resultados_archivos,
        "resultados_lectura": resultados_lectura,
        "resultados_proveedores": resultados_proveedores,
        "resultados_organizacion": resultados_organizacion,
    }

