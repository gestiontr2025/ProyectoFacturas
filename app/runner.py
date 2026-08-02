"""Punto central de comandos del Proyecto Facturas.

El runner interpreta los argumentos de la terminal y delega cada operación en
un módulo especializado. Mantener esta capa breve hace que agregar un comando
nuevo no mezcle su implementación con las demás tareas.
"""

from __future__ import annotations

import argparse

from infrastructure import configure_logging, get_logger
from state import EmailHistory

import config
from app.gmail_workflow import run_gmail_processing
from app.pending_reprocessor import mostrar_resumen_reprocesamiento, reprocesar_pendientes
from suppliers import normalize_supplier_folders
from storage import audit_organized_invoice_dates, cleanup_exact_invoice_duplicates
from taxes import export_supplier_tax_profile

logger = get_logger(__name__)


def _crear_argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Descarga y organiza facturas de Gmail.")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument(
        "--full-scan",
        action="store_true",
        help="Recorre todo Gmail y omite los correos ya completados.",
    )
    modes.add_argument(
        "--reprocess-pending",
        action="store_true",
        help="Analiza los PDF de _Pendientes sin conectarse a Gmail.",
    )
    modes.add_argument(
        "--normalize-supplier-folders",
        action="store_true",
        help="Une carpetas históricas que representan al mismo proveedor.",
    )
    modes.add_argument(
        "--deduplicate-invoices",
        action="store_true",
        help="Busca copias idénticas entre facturas ya organizadas.",
    )
    modes.add_argument(
        "--audit-organized-dates",
        action="store_true",
        help="Revisa fechas de facturas organizadas; requiere --apply para mover archivos.",
    )
    modes.add_argument(
        "--export-supplier-tax-profile",
        action="store_true",
        help="Genera en el Escritorio un Excel con los impuestos observados por proveedor.",
    )
    modes.add_argument(
        "--email-history",
        action="store_true",
        help="Muestra un resumen del historial local de correos.",
    )
    modes.add_argument(
        "--reset-email-history",
        action="store_true",
        help="Prepara el reinicio del historial; requiere --apply para ejecutarlo.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Confirma una operación destructiva que por defecto es vista previa.",
    )
    return parser.parse_args()


def main() -> None:
    argumentos = _crear_argumentos()
    log_file = configure_logging(config.LOG_FOLDER, config.LOG_LEVEL)
    logger.info("Aplicación iniciada. Archivo de log: %s", log_file)

    if argumentos.reprocess_pending:
        resultados = reprocesar_pendientes()
        mostrar_resumen_reprocesamiento(resultados)
        return

    if argumentos.deduplicate_invoices:
        _run_deduplication(apply=argumentos.apply)
        return

    if argumentos.normalize_supplier_folders:
        _run_supplier_normalization()
        return

    if argumentos.audit_organized_dates:
        _run_date_audit(apply=argumentos.apply)
        return

    if argumentos.export_supplier_tax_profile:
        _run_supplier_tax_profile_export()
        return

    history = EmailHistory(config.STATE_DB_PATH)

    if argumentos.email_history:
        _show_email_history(history)
        return

    if argumentos.reset_email_history:
        _reset_email_history(history, apply=argumentos.apply)
        return

    try:
        run_gmail_processing(full_scan=argumentos.full_scan)
    except Exception as error:
        # El flujo Gmail ya registró el traceback. Aquí mostramos un mensaje
        # breve para el usuario sin duplicar toda la lógica de diagnóstico.
        print("\nSE PRODUJO UN ERROR GENERAL")
        print(error)


def _show_email_history(history: EmailHistory) -> None:
    summary = history.summary()
    print("\n" + "=" * 50)
    print("HISTORIAL DE CORREOS")
    print("=" * 50)
    print(f"Total registrado: {summary['total']}")
    print(f"Procesados con PDF: {summary['processed']}")
    print(f"Procesados sin PDF: {summary['no_pdf']}")
    print(f"Errores pendientes de reintento: {summary['error']}")
    print(f"Base de datos: {config.STATE_DB_PATH}")
    print("=" * 50)


def _reset_email_history(history: EmailHistory, *, apply: bool) -> None:
    summary = history.summary()
    print("\n" + "=" * 50)
    print("REINICIO DEL HISTORIAL DE CORREOS")
    print("=" * 50)
    print(f"Registros actuales: {summary['total']}")
    if not apply:
        print("Vista previa: no se eliminó ningún registro.")
        print("Usá --reset-email-history --apply para confirmar.")
    else:
        removed = history.reset()
        print(f"Historial reiniciado. Registros eliminados: {removed}")
    print("=" * 50)


def _run_deduplication(*, apply: bool) -> None:
    resultados = cleanup_exact_invoice_duplicates(config.SAVE_FOLDER, apply=apply)
    print("\n" + "=" * 50)
    print("DEDUPLICACIÓN DE FACTURAS")
    print("=" * 50)
    if not resultados:
        print("No se encontraron copias idénticas entre las facturas organizadas.")
    elif not apply:
        print("Modo vista previa: no se eliminó ningún archivo.")
        print("Volvé a ejecutar con --apply para confirmar la limpieza.")
    for resultado in resultados:
        print(f"\nEstado: {resultado.status}")
        print(f"Copia redundante: {resultado.duplicate}")
        print(f"Copia conservada: {resultado.survivor}")
        if resultado.detail:
            print(f"Detalle: {resultado.detail}")
    print("\n" + "=" * 50)


def _run_supplier_normalization() -> None:
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


def _run_date_audit(*, apply: bool) -> None:
    resultados = audit_organized_invoice_dates(config.SAVE_FOLDER, apply=apply)
    print("\n" + "=" * 50)
    print("AUDITORÍA DE FECHAS ORGANIZADAS")
    print("=" * 50)
    if not resultados:
        print("No se encontraron facturas con fechas inconsistentes.")
    elif not apply:
        print("Modo vista previa: no se movió ningún archivo.")
        print("Usá --audit-organized-dates --apply para confirmar.")
    for resultado in resultados:
        print(f"\nEstado: {resultado.status}")
        print(f"Origen: {resultado.source}")
        if resultado.destination:
            print(f"Destino: {resultado.destination}")
        if resultado.detail:
            print(f"Detalle: {resultado.detail}")
    print("\n" + "=" * 50)


def _run_supplier_tax_profile_export() -> None:
    """Generar el perfil impositivo acumulado de proveedores organizados."""
    result = export_supplier_tax_profile(config.SAVE_FOLDER)
    print("\n" + "=" * 50)
    print("EXPORTACIÓN DEL PERFIL IMPOSITIVO")
    print("=" * 50)
    print(f"Facturas analizadas: {result.invoices_analyzed}")
    print(f"Proveedores únicos: {result.suppliers}")
    print(f"PDF omitidos por datos insuficientes o error: {result.invoices_skipped}")
    print(f"Archivo generado: {result.output_path}")
    print("=" * 50)
