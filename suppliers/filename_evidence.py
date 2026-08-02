"""Evidencia secundaria de proveedor basada en nombres de adjuntos.

La razón social y el CUIT dentro del PDF siguen siendo la fuente principal.
Este módulo contiene solamente patrones de alta especificidad para familias
de archivos cuyo encabezado está dibujado como imagen y no aparece en el
texto extraído.

Las reglas no devuelven una razón social inventada: devuelven un identificador
canónico que ya debe existir en :mod:`supplier_catalog`.
"""

from pathlib import Path
import re
from typing import Optional

import business_config
import supplier_catalog


# Cada patrón debe ser suficientemente específico para no confundir archivos
# genéricos. La lista se mantiene pequeña y acompañada por pruebas reales.
_FILENAME_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    # Frigorífico Los Prados exporta sus facturas con esta estructura. El PDF
    # contiene los importes y datos fiscales como texto, pero el logotipo y el
    # CUIT emisor forman parte de una capa gráfica que pypdf no recupera.
    (re.compile(r"^FA_002000\d{6}_\d{8}_011454_", re.IGNORECASE), "frigorifico_los_prados"),
    # La misma empresa utiliza CA_ para notas de crédito. El resto de la
    # estructura (punto de venta 0020 y código interno 011454) es idéntica.
    (re.compile(r"^CA_002000\d{6}_\d{8}_011454_", re.IGNORECASE), "frigorifico_los_prados"),
    # Familias observadas en adjuntos cuyo encabezado comercial es una imagen.
    # Se exige el prefijo completo y el punto de venta constante para evitar
    # asignaciones por un nombre genérico como ``Factura A``.
    (re.compile(r"^FACA00031\d{8}(?:_ORIG)?\.PDF$", re.IGNORECASE), "gifel_s_r_l"),
    (re.compile(r"^FACB00007\d{8}\.PDF$", re.IGNORECASE), "el_nuevo_emporio_sa"),
    (re.compile(r"^FACA000(?:07|10)\d{8}\.PDF$", re.IGNORECASE), "el_nuevo_emporio_sa"),
    (re.compile(r"^N[ _-]*CB00010\d{8}\.PDF$", re.IGNORECASE), "el_nuevo_emporio_sa"),
    (re.compile(r"^\d{14}_COMPROBANTE-FCVTA-A-2-\d+\.PDF$", re.IGNORECASE), "buenos_ayres_vinos_y_bebidas_s_a"),
)


def detectar_identificador_por_nombre(nombre_archivo: str) -> Optional[str]:
    """Devolver proveedor canónico solo ante evidencia inequívoca.

    Se utilizan dos fuentes defensivas:

    1. Patrones históricos muy específicos para familias cuyo encabezado es
       una imagen.
    2. Un CUIT de once dígitos incluido en el nombre del archivo, siempre que
       pertenezca al catálogo y no sea el CUIT de la empresa receptora.

    Esta segunda regla permite reconocer exportaciones ARCA como
    ``30711183058_01_0003_00063985.pdf`` sin crear una excepción por cada
    proveedor recurrente.
    """

    nombre = Path(nombre_archivo).name
    for patron, identificador in _FILENAME_PATTERNS:
        if patron.search(nombre):
            return identificador

    # Los nombres exportados por ARCA suelen comenzar con el CUIT emisor.
    # Buscamos grupos exactos de once dígitos y consultamos la fuente única de
    # verdad. Nunca utilizamos el CUIT receptor como evidencia de proveedor.
    for cuit in re.findall(r"(?<!\d)(\d{11})(?!\d)", nombre):
        if business_config.es_cuit_receptor(cuit):
            continue
        proveedor = supplier_catalog.buscar_proveedor_por_cuit(cuit)
        if proveedor is not None:
            return proveedor.identificador

    return None
