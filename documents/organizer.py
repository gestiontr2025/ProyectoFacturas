"""Archivo seguro de documentos que no pertenecen al flujo fiscal."""

from pathlib import Path

from documents.classifier import TipoDocumento
from storage import FileMoveResult, safe_archive_file


FOLDERS_BY_TYPE = {
    TipoDocumento.LISTA_PRECIOS: "Listas_de_precios",
    TipoDocumento.COMPROBANTE_PAGO: "Comprobantes_de_pago",
    TipoDocumento.ORDEN_PAGO: "Ordenes_de_pago",
    TipoDocumento.RRHH_ALTAS_BAJAS: "Recursos_Humanos/Altas_y_Bajas",
    TipoDocumento.RRHH_LIQUIDACIONES: "Recursos_Humanos/Liquidaciones",
    TipoDocumento.RRHH_RECIBOS_LEGAJOS: "Recursos_Humanos/Recibos_y_Legajos",
    TipoDocumento.RETENCIONES_TRANSFERENCIAS: "Retenciones_y_Transferencias",
    TipoDocumento.ESTADO_CUENTA: "Estados_de_cuenta",
    TipoDocumento.MENUS_CARTAS: "Menus_y_Cartas",
    TipoDocumento.INSTRUCTIVO: "Instructivos",
    TipoDocumento.ADMINISTRATIVO: "Administrativos",
    TipoDocumento.COMUNICACION: "Comunicaciones",
    TipoDocumento.REMITO_RECIBO: "Remitos_y_recibos",
    TipoDocumento.IMPUESTOS_SERVICIOS: "Impuestos_y_servicios",
    TipoDocumento.OPERATIVO: "Operativos",
    TipoDocumento.CONSORCIO: "Consorcio_y_gastos_comunes",
}


def archivar_otro_documento(
    ruta_pdf: Path | str,
    carpeta_raiz: Path | str,
    tipo: TipoDocumento,
) -> FileMoveResult:
    """Archivar un documento no fiscal aplicando deduplicación por contenido.

    La función solo admite categorías con una carpeta definida. Un documento
    desconocido debe permanecer en ``_Pendientes`` para revisión humana.
    """

    folder = FOLDERS_BY_TYPE.get(tipo)
    if folder is None:
        raise ValueError(f"No existe una carpeta configurada para {tipo!s}.")

    destination = Path(carpeta_raiz) / "_OtrosDocumentos" / folder
    return safe_archive_file(ruta_pdf, destination)


def archivar_lista_precios(ruta_pdf, carpeta_raiz) -> Path:
    """Compatibilidad con código anterior que espera únicamente una ruta."""

    return archivar_otro_documento(
        ruta_pdf, carpeta_raiz, TipoDocumento.LISTA_PRECIOS
    ).destination
