"""Flujo de procesamiento incremental y completo de Gmail.

Este módulo concentra la coordinación específica de Gmail. ``runner.py`` solo
decide qué comando pidió el usuario, mientras que este archivo administra:

- la selección de correos;
- la consulta del historial persistente;
- la omisión de mensajes ya completados;
- el registro inmediato de éxitos y errores.
"""

from __future__ import annotations

from dataclasses import dataclass

from infrastructure import get_logger
from state import EmailHistory, EmailIdentity

import config
import console_output
import gmail_client
from app import email_processor, email_selection, presentation

logger = get_logger(__name__)


@dataclass
class GmailRunMetrics:
    """Contadores principales de una ejecución contra Gmail."""

    found: int = 0
    selected: int = 0
    skipped: int = 0
    processed: int = 0
    errors: int = 0


def run_gmail_processing(*, full_scan: bool = False) -> GmailRunMetrics:
    """Procesar Gmail respetando el historial local.

    En modo normal solo se considera la ventana configurada mediante
    ``EMAIL_PROCESSING_LIMIT``. En modo completo se recorre todo el buzón desde
    el correo más reciente al más antiguo. En ambos casos se omiten los mensajes
    que ya terminaron correctamente en una ejecución anterior.
    """

    # Las credenciales solo son obligatorias para los modos que realmente
    # se conectan a Gmail. Así, comandos locales como --help o --email-history
    # continúan funcionando aunque .env todavía no esté configurado.
    config.validar_configuracion()

    history = EmailHistory(config.STATE_DB_PATH)
    metrics = GmailRunMetrics()
    connection = None

    presentation.mostrar_informacion_proyecto()
    presentation.mostrar_configuracion()

    try:
        mode = "full_scan" if full_scan else "incremental"
        logger.info("Modo Gmail iniciado: %s", mode)
        connection = gmail_client.conectar()
        logger.info("Conexión con Gmail establecida")

        all_ids = gmail_client.buscar_todos_los_correos(connection)
        metrics.found = len(all_ids)
        presentation.mostrar_resultado_busqueda(all_ids)

        if not all_ids:
            console_output.linea_en_blanco()
            console_output.mostrar_mensaje("No se encontraron correos para procesar.")
            return metrics

        if full_scan:
            selected_ids = list(reversed(all_ids))
        else:
            selected_ids = email_selection.seleccionar_correos_recientes(
                all_ids,
                config.EMAIL_PROCESSING_LIMIT,
            )

        metrics.selected = len(selected_ids)
        presentation.mostrar_correos_seleccionados(metrics.selected)

        all_file_results = []
        all_read_results = []
        all_supplier_results = []

        for position, email_id in enumerate(selected_ids, start=1):
            identity = _safe_identity(connection, email_id)

            if history.is_completed(identity.source_key):
                metrics.skipped += 1
                logger.debug(
                    "Correo omitido por historial: %s - %s",
                    identity.source_key,
                    identity.subject,
                )
                continue

            presentation.mostrar_inicio_correo(position, metrics.selected, email_id)

            try:
                result = email_processor.procesar_correo(connection, email_id)
                all_file_results.extend(result["resultados_archivos"])
                all_read_results.extend(result["resultados_lectura"])
                all_supplier_results.extend(result["resultados_proveedores"])

                pdf_count = len(result["resultados_archivos"])
                history.mark_success(identity, pdf_count=pdf_count)
                metrics.processed += 1
                logger.info(
                    "Correo completado: %s; pdf_count=%s",
                    identity.source_key,
                    pdf_count,
                )
            except Exception as error:
                history.mark_error(identity, error)
                metrics.errors += 1
                logger.exception("Error procesando %s", identity.source_key)
                presentation.mostrar_error_correo(email_id, error)

        presentation.mostrar_resumen_final(
            metrics.selected,
            metrics.processed,
            metrics.errors,
            all_file_results,
            all_read_results,
            all_supplier_results,
        )
        _show_history_metrics(metrics)
        return metrics

    except Exception:
        logger.exception("Error general no controlado durante el flujo Gmail")
        raise
    finally:
        if connection is not None:
            try:
                connection.logout()
                console_output.linea_en_blanco()
                logger.info("Conexión con Gmail cerrada correctamente")
                console_output.mostrar_mensaje("Conexión cerrada correctamente.")
            except Exception as close_error:
                logger.exception("No fue posible cerrar la conexión con Gmail")
                console_output.linea_en_blanco()
                console_output.mostrar_mensaje(
                    "No fue posible cerrar la conexión de forma normal."
                )
                console_output.mostrar_mensaje(close_error)


def _safe_identity(connection, email_id: bytes) -> EmailIdentity:
    """Obtener una identidad o crear un respaldo para registrar un fallo.

    El respaldo por número de secuencia no es estable entre sesiones, pero
    permite que un error de metadatos quede documentado en lugar de detener todo
    el lote. Gmail normalmente proporciona ``X-GM-MSGID`` y evita este caso.
    """

    try:
        return gmail_client.obtener_identidad_correo(connection, email_id)
    except Exception as error:
        logger.warning(
            "No se pudo obtener X-GM-MSGID para %r: %s",
            email_id,
            error,
        )
        return EmailIdentity(
            source_key=f"imap-sequence:{email_id.decode(errors='replace')}",
            subject="Identidad no disponible",
        )


def _show_history_metrics(metrics: GmailRunMetrics) -> None:
    print("\n" + "=" * 50)
    print("HISTORIAL DE CORREOS")
    print("=" * 50)
    print(f"Correos encontrados: {metrics.found}")
    print(f"Correos considerados: {metrics.selected}")
    print(f"Omitidos por estar completados: {metrics.skipped}")
    print(f"Procesados en esta ejecución: {metrics.processed}")
    print(f"Errores registrados para reintento: {metrics.errors}")
    print("=" * 50)
