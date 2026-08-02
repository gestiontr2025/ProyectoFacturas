"""Selection of canonical supplier names for folders and PDF files."""

from models import Supplier


def obtener_nombre_para_carpeta(resultado_proveedor: dict) -> str:
    """Return the supplier's stable canonical folder name.

    The detector can recognize a company through its legal name, trade name,
    CUIT or aliases. All those paths are adapted to ``Supplier`` and converge
    on one folder name.
    """
    return Supplier.from_detection_result(resultado_proveedor).folder_name


def obtener_razon_social_fiscal(resultado_proveedor: dict) -> str:
    """Return the legal name that must remain in the PDF filename."""
    supplier = Supplier.from_detection_result(resultado_proveedor)
    return str(supplier.legal_name or "").strip()
