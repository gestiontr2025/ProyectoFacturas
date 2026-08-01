"""Archivo seguro de documentos que no pertenecen al flujo de facturas."""

from pathlib import Path
import shutil


def archivar_lista_precios(ruta_pdf, carpeta_raiz) -> Path:
    """Mover una lista de precios fuera de ``_Pendientes`` sin sobrescribirla."""

    origen = Path(ruta_pdf)
    destino_dir = Path(carpeta_raiz) / "_OtrosDocumentos" / "Listas_de_precios"
    destino_dir.mkdir(parents=True, exist_ok=True)
    destino = destino_dir / origen.name

    if destino.exists():
        return destino

    shutil.move(str(origen), str(destino))
    return destino
