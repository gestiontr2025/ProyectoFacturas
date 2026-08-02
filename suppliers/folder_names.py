"""Nombres canónicos para las carpetas de proveedores.

Una misma empresa puede aparecer con una razón social extensa, un nombre
comercial y distintos alias. Todos esos datos ayudan a reconocerla, pero no
deben producir carpetas diferentes.

Este módulo es la única fuente de verdad para decidir el nombre físico de la
carpeta. El nombre fiscal continúa utilizándose dentro del nombre del PDF.
"""

from __future__ import annotations

from invoices.text_normalization import normalizar_componente_ruta


# Los valores se escriben ya normalizados para que sean estables en Windows,
# Linux y macOS. La clave es el identificador interno devuelto por el detector.
_CANONICAL_FOLDER_BY_IDENTIFIER: dict[str, str] = {
    "all_online_solutions": "Colppy",
    "arta_verduleros": "Arta Verduleros",
    "el_criollo": "El Criollo",
}


def get_canonical_folder_name(
    identifier: str | None,
    display_name: str | None,
    legal_name: str | None,
) -> str:
    """Return one stable folder name for a recognized supplier.

    Priority:
        1. An explicit canonical name associated with the internal identifier.
        2. The supplier's trade name.
        3. The legal name.
        4. A defensive placeholder when no identity is available.

    The function returns a path-safe component. Callers therefore do not need
    to normalize the same value again, avoiding subtly different rules in
    different parts of the application.
    """
    normalized_identifier = str(identifier or "").strip().lower()
    explicit_name = _CANONICAL_FOLDER_BY_IDENTIFIER.get(normalized_identifier)
    if explicit_name:
        return explicit_name

    preferred_name = display_name or legal_name or "PROVEEDOR_DESCONOCIDO"
    return str(preferred_name).strip()


def get_known_folder_aliases() -> dict[str, str]:
    """Return legacy folder names mapped to their canonical destination.

    These aliases are used only by the migration command. New invoices should
    already be written directly to the canonical folder.
    """
    return {
        "ARTA_DE_GONZALEZ_S_R_L": "ARTA_VERDULEROS",
        "ARTA_VERDULEROS": "ARTA_VERDULEROS",
        "DISTRIBUIDORA_EL_CRIOLLO_SRL": "EL_CRIOLLO",
        "EL_CRIOLLO": "EL_CRIOLLO",
        "ALL_ONLINE_SOLUTIONS_S_A_U": "COLPPY",
        "COLPPY": "COLPPY",
    }
