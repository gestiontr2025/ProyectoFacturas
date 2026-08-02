"""Resolver el nombre canónico de la carpeta de cada proveedor.

El nombre explícito de carpeta vive en ``supplier_catalog.json`` junto con la
identidad fiscal. Así evitamos mantener la misma decisión en Python y JSON.
"""

from __future__ import annotations


def get_canonical_folder_name(
    identifier: str | None,
    display_name: str | None,
    legal_name: str | None,
) -> str:
    """Devolver un único nombre estable para la carpeta física.

    La importación se realiza dentro de la función para evitar un ciclo de
    importaciones: ``supplier_catalog`` crea los proveedores y los modelos de
    dominio consultan este módulo al organizar un documento.
    """
    normalized_identifier = str(identifier or "").strip()
    if normalized_identifier:
        import supplier_catalog

        supplier = supplier_catalog.obtener_proveedor(normalized_identifier)
        if supplier and supplier.nombre_carpeta:
            return supplier.nombre_carpeta

    return str(display_name or legal_name or "PROVEEDOR_DESCONOCIDO").strip()


def get_known_folder_aliases() -> dict[str, str]:
    """Devolver alias históricos usados por el comando de migración."""
    return {
        "ARTA_DE_GONZALEZ_S_R_L": "ARTA_VERDULEROS",
        "ARTA_VERDULEROS": "ARTA_VERDULEROS",
        "DISTRIBUIDORA_EL_CRIOLLO_SRL": "EL_CRIOLLO",
        "EL_CRIOLLO": "EL_CRIOLLO",
        "ALL_ONLINE_SOLUTIONS_S_A_U": "COLPPY",
        "COLPPY": "COLPPY",
    }
