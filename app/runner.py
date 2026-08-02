"""Coordinador principal de la aplicación.

El coordinador decide qué modo ejecutar, pero delega cada tarea concreta en
módulos especializados. Puede descargar correos o reprocesar archivos locales.
"""

import argparse

import config
import console_output
import gmail_client

from app import email_processor, email_selection, presentation
from suppliers import normalize_supplier_folders
from storage import cleanup_exact_invoice_duplicates

from app.pending_reprocessor import (
    mostrar_resumen_reprocesamiento,
    reprocesar_pendientes,
)


def _crear_argumentos() -> argparse.Namespace:
    """Leer opciones de terminal sin mezclar esta tarea con la lógica principal."""

    parser = argparse.ArgumentParser(description="Descarga y organiza facturas de Gmail.")
    parser.add_argument(
        "--reprocess-pending",
        action="store_true",
        help="Analiza los PDF de _Pendientes sin conectarse a Gmail.",
    )
    parser.add_argument(
        "--normalize-supplier-folders",
        action="store_true",
        help="Une carpetas históricas que representan al mismo proveedor.",
    )
    parser.add_argument(
        "--deduplicate-invoices",
        action="store_true",
        help="Busca copias idénticas entre facturas ya organizadas.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Aplica una operación destructiva que, sin esta opción, es solo vista previa.",
    )
    return parser.parse_args()


def main():
    """Coordinar el modo solicitado por el usuario."""

    argumentos = _crear_argumentos()
    if argumentos.reprocess_pending:
        resultados = reprocesar_pendientes()
        mostrar_resumen_reprocesamiento(resultados)
        return

    if argumentos.deduplicate_invoices:
        resultados = cleanup_exact_invoice_duplicates(
            config.SAVE_FOLDER,
            apply=argumentos.apply,
        )
        print("\n" + "=" * 50)
        print("DEDUPLICACIÓN DE FACTURAS")
        print("=" * 50)
        if not resultados:
            print("No se encontraron copias idénticas entre las facturas organizadas.")
        elif not argumentos.apply:
            print("Modo vista previa: no se eliminó ningún archivo.")
            print("Volvé a ejecutar con --apply para confirmar la limpieza.")
        for resultado in resultados:
            print(f"\nEstado: {resultado.status}")
            print(f"Copia redundante: {resultado.duplicate}")
            print(f"Copia conservada: {resultado.survivor}")
            if resultado.detail:
                print(f"Detalle: {resultado.detail}")
        print("\n" + "=" * 50)
        return

    if argumentos.normalize_supplier_folders:
        resultados = normalize_supplier_folders(config.SAVE_FOLDER)
        print("\n" + "=" * 50)
        print("NORMALIZACIÓN DE CARPETAS DE PROVEEDORES")
        print("=" * 50)
        if not resultados:
            print("No se encontraron carpetas conocidas para normalizar.")
        for resultado in resultados:
            print(f"\nEstado: {resultado.status}")
            print(f"Origen: {resultado.source}")
            print(f"Destino: {resultado.destination}")
            if resultado.detail:
                print(f"Detalle: {resultado.detail}")
        print("\n" + "=" * 50)
        return

    presentation.mostrar_informacion_proyecto()
    presentation.mostrar_configuracion()
    conexion = None

    try:
        conexion = gmail_client.conectar()
        identificadores_correos = gmail_client.buscar_todos_los_correos(conexion)
        presentation.mostrar_resultado_busqueda(identificadores_correos)

        if not identificadores_correos:
            console_output.linea_en_blanco()
            console_output.mostrar_mensaje("No se encontraron correos para procesar.")
            return

        correos_seleccionados = email_selection.seleccionar_correos_recientes(
            identificadores_correos,
            config.EMAIL_PROCESSING_LIMIT,
        )
        cantidad_seleccionada = len(correos_seleccionados)
        presentation.mostrar_correos_seleccionados(cantidad_seleccionada)

        cantidad_procesada = 0
        cantidad_errores = 0
        todos_los_resultados_archivos = []
        todos_los_resultados_lectura = []
        todos_los_resultados_proveedores = []

        for numero_correo, id_correo in enumerate(correos_seleccionados, start=1):
            presentation.mostrar_inicio_correo(
                numero_correo,
                cantidad_seleccionada,
                id_correo,
            )
            try:
                resultado_correo = email_processor.procesar_correo(conexion, id_correo)
                todos_los_resultados_archivos.extend(resultado_correo["resultados_archivos"])
                todos_los_resultados_lectura.extend(resultado_correo["resultados_lectura"])
                todos_los_resultados_proveedores.extend(resultado_correo["resultados_proveedores"])
                cantidad_procesada += 1
            except Exception as error_correo:
                cantidad_errores += 1
                presentation.mostrar_error_correo(id_correo, error_correo)

        presentation.mostrar_resumen_final(
            cantidad_seleccionada,
            cantidad_procesada,
            cantidad_errores,
            todos_los_resultados_archivos,
            todos_los_resultados_lectura,
            todos_los_resultados_proveedores,
        )
    except Exception as error:
        console_output.mostrar_error("SE PRODUJO UN ERROR GENERAL", error)
    finally:
        if conexion is not None:
            try:
                conexion.logout()
                console_output.linea_en_blanco()
                console_output.mostrar_mensaje("Conexión cerrada correctamente.")
            except Exception as error_cierre:
                console_output.linea_en_blanco()
                console_output.mostrar_mensaje("No fue posible cerrar la conexión de forma normal.")
                console_output.mostrar_mensaje(error_cierre)
