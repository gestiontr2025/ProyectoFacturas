"""Selección del nombre de proveedor usado en carpetas y archivos.

Una empresa puede tener una razón social extensa y un nombre comercial mucho
más reconocible. El proyecto conserva ambos conceptos separados:

- El nombre del archivo usa la razón social fiscal, porque describe al emisor
  legal del comprobante.
- La carpeta puede usar el nombre de fantasía, porque facilita la navegación
  cotidiana para una persona.

Ejemplo:
    Razón social: ALL ONLINE SOLUTIONS S. A. U.
    Nombre de fantasía: Colppy
    Carpeta final: ``COLPPY``
"""


def obtener_nombre_para_carpeta(resultado_proveedor: dict) -> str:
    """Elegir nombre de fantasía y usar la razón social como respaldo.

    El detector ya relaciona alias, CUIT y razón social. Centralizar aquí esta
    decisión evita introducir excepciones como ``if proveedor == ...`` dentro
    del organizador y permite que futuros proveedores aprovechen su nombre
    comercial sin cambiar el flujo principal.
    """
    if not resultado_proveedor:
        return "PROVEEDOR_DESCONOCIDO"

    nombre_fantasia = str(resultado_proveedor.get("nombre_fantasia") or "").strip()
    if nombre_fantasia:
        return nombre_fantasia

    return str(resultado_proveedor.get("razon_social_encontrada") or "").strip()


def obtener_razon_social_fiscal(resultado_proveedor: dict) -> str:
    """Devolver la razón social que debe figurar en el nombre del PDF."""
    return str(resultado_proveedor.get("razon_social_encontrada") or "").strip()
