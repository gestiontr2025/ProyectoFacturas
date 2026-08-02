"""Creación de carpetas y movimiento seguro de facturas."""

from pathlib import Path

from invoices.filename_builder import convertir_fecha
from invoices.text_normalization import normalizar_componente_ruta
from storage import safe_move_invoice


def construir_carpeta_final(raiz, razon_social_proveedor: str, fecha_emision: str) -> Path:
    """Construir ``Facturas/proveedor/año/mes`` usando la fecha de emisión."""
    fecha = convertir_fecha(fecha_emision)
    proveedor = normalizar_componente_ruta(razon_social_proveedor)
    return Path(raiz) / proveedor / f"{fecha:%Y}" / f"{fecha:%m}"


def mover_a_destino_final(ruta_actual, carpeta_final, nombre_final):
    """Mover una factura aplicando deduplicación por contenido e identidad.

    La función conserva la API histórica y devuelve solamente la ruta final.
    Internamente delega en ``storage.safe_move_invoice``, que elimina una copia
    temporal solo cuando existe otra copia binariamente idéntica.
    """

    result = safe_move_invoice(ruta_actual, carpeta_final, nombre_final)
    return result.destination
