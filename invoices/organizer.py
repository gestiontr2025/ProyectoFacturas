"""Creación de carpetas y movimiento seguro de facturas."""

from pathlib import Path
import shutil

from invoices.filename_builder import convertir_fecha
from invoices.text_normalization import normalizar_componente_ruta


def construir_carpeta_final(raiz, razon_social_proveedor: str, fecha_emision: str) -> Path:
    """Construir ``Facturas/proveedor/año/mes`` usando la fecha de emisión."""
    fecha = convertir_fecha(fecha_emision)
    proveedor = normalizar_componente_ruta(razon_social_proveedor)
    return Path(raiz) / proveedor / f"{fecha:%Y}" / f"{fecha:%m}"


def obtener_ruta_sin_colision(ruta_deseada: Path) -> Path:
    """Evitar sobrescribir un archivo diferente que tenga el mismo nombre.

    Si el nombre ya existe, se agregan sufijos ``_2``, ``_3`` y así
    sucesivamente. Preservar ambos documentos es más seguro que reemplazar uno
    silenciosamente.
    """
    if not ruta_deseada.exists():
        return ruta_deseada

    contador = 2
    while True:
        candidata = ruta_deseada.with_name(
            f"{ruta_deseada.stem}_{contador}{ruta_deseada.suffix}"
        )
        if not candidata.exists():
            return candidata
        contador += 1


def mover_a_destino_final(ruta_actual, carpeta_final, nombre_final) -> Path:
    """Mover el PDF desde `_Pendientes` hasta su ubicación definitiva."""
    origen = Path(ruta_actual)
    destino_dir = Path(carpeta_final)
    destino_dir.mkdir(parents=True, exist_ok=True)
    destino = obtener_ruta_sin_colision(destino_dir / nombre_final)
    return Path(shutil.move(str(origen), str(destino)))
