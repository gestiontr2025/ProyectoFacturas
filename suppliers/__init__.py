"""Herramientas relacionadas con la identidad canónica de proveedores.

El catálogo y el detector históricos permanecen en módulos de nivel superior
mientras se completa su futura refactorización. Este paquete concentra desde
ahora las decisiones que afectan a la organización física de archivos.
"""

from suppliers.folder_names import get_canonical_folder_name
from suppliers.folder_migration import normalize_supplier_folders

__all__ = ["get_canonical_folder_name", "normalize_supplier_folders"]
