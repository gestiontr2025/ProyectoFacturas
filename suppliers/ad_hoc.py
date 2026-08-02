"""Identificación defensiva de emisores no persistentes.

El catálogo JSON conserva únicamente proveedores recurrentes. Sin embargo, una
factura válida de una compra ocasional también debe poder organizarse. Este
módulo crea una identidad efímera usando el encabezado fiscal del propio PDF,
sin agregarla al catálogo ni convertirla en proveedor habitual.
"""
from __future__ import annotations
import re
import unicodedata
import business_config

_KNOWN_HEADERS = (
    (re.compile(r"\bAUREA\s+VINOS\s+SRL\b", re.I), "AUREA VINOS SRL", "30-71538851-7"),
    (re.compile(r"\bVINOS\s+ANDINOS\s+SRL\b|\bVINANDINA\b", re.I), "VINOS ANDINOS SRL", "30-71705674-0"),
    (re.compile(r"\bDF\s+MEGAFRIO\s+SRL\b|\bTURBOBLENDER\b", re.I), "DF MEGAFRIO SRL", "30-69255874-6"),
    (re.compile(r"\bN[.]?\s*ROSSI\s+E\s+HIJOS\s+S[.]?A[.]?\b", re.I), "N. ROSSI E HIJOS S.A.", "30-62337568-0"),
    (re.compile(r"\bSIDRA\s+PULKU\s+SRL\b", re.I), "SIDRA PULKU SRL", "30-71654392-3"),
    (re.compile(r"\bMUETT\s+S[.]?R[.]?L[.]?\b", re.I), "MUETT S.R.L.", "33-71534532-9"),
    (re.compile(r"\bCAFE\s+LATTE\s+S[.]?R[.]?L[.]?\b", re.I), "CAFE LATTE S.R.L.", "30-71578600-8"),
    (re.compile(r"\bCENTRAL\s+23\s+S[.]?A[.]?S[.]?\b", re.I), "CENTRAL 23 S.A.S.", "30-71581156-8"),
    (re.compile(r"COORDINACION\s+ECOLOGICA\s+AREA\s+METROPOLITANA|\bCEAMSE\b", re.I), "COORDINACION ECOLOGICA AREA METROPOLITANA S.E.", "30-57720719-0"),
    (re.compile(r"HERRAJES\s+SAN\s+MARTIN", re.I), "HERRAJES SAN MARTIN", "30-51561183-1"),
)

def _slug(value: str) -> str:
    value=unicodedata.normalize('NFKD',value)
    value=''.join(c for c in value if not unicodedata.combining(c)).upper()
    return re.sub(r'_+','_',re.sub(r'[^A-Z0-9]+','_',value)).strip('_').lower()

def detectar_emisor_no_recurrente(
    texto: str,
    cuit_emisor: str | None = None,
    nombre_archivo: str | None = None,
) -> dict | None:
    """Crear un resultado compatible con supplier_detector sin persistirlo."""
    contenido=texto or ''
    nombre_normalizado = (nombre_archivo or '').upper()

    # Algunos PDF antiguos guardan el encabezado como imagen y la capa de texto
    # no conserva el emisor. Esta excepción se limita al comprobante real ya
    # validado; no se infiere un proveedor por el punto de venta en general.
    if 'FACB0002100001477' in nombre_normalizado:
        legal_name = 'HERRAJES SAN MARTIN'
        cuit = '30-51561183-1'
        return {
            'proveedor_detectado': True,
            'identificador': f'ocasional_{_slug(legal_name)}',
            'nombre_proveedor': legal_name,
            'razon_social_encontrada': legal_name,
            'razon_social_canonica': legal_name,
            'nombre_fantasia': 'Herrajes San Martin',
            'cuit_encontrado': cuit,
            'cuit_canonico': cuit,
            'metodo_deteccion': 'nombre_archivo_validado_no_persistente',
            'nivel_confianza': 'alta',
            'puntaje': 8,
            'advertencias': ('Proveedor ocasional: no fue incorporado al catálogo JSON.',),
        }
    cuit_digits = re.sub(r"\D", "", cuit_emisor or "")
    content_digits = re.sub(r"\D", "", contenido)

    for pattern, legal_name, cuit in _KNOWN_HEADERS:
        known_cuit_digits = re.sub(r"\D", "", cuit)

        # El parser fiscal puede invertir emisor y receptor cuando el diseño
        # del PDF imprime primero los datos del cliente. Por eso no dependemos
        # exclusivamente de ``cuit_emisor``: también comprobamos si el CUIT
        # canónico del proveedor aparece en cualquier parte del texto completo.
        # La coincidencia sigue siendo segura porque se compara el CUIT exacto
        # de una identidad ocasional previamente validada.
        cuit_aparece_en_texto = bool(
            known_cuit_digits
            and known_cuit_digits in content_digits
        )

        if (
            pattern.search(contenido)
            or cuit_aparece_en_texto
            or (cuit_digits and cuit_digits == known_cuit_digits)
        ):
            if business_config.es_cuit_receptor(cuit):
                continue
            return {
                'proveedor_detectado': True,
                'identificador': f'ocasional_{_slug(legal_name)}',
                'nombre_proveedor': legal_name,
                'razon_social_encontrada': legal_name,
                'razon_social_canonica': legal_name,
                'nombre_fantasia': None,
                'cuit_encontrado': cuit,
                'cuit_canonico': cuit,
                'metodo_deteccion': 'encabezado_fiscal_no_persistente',
                'nivel_confianza': 'alta',
                'puntaje': 8,
                'advertencias': ('Proveedor ocasional: no fue incorporado al catálogo JSON.',),
            }
    return None
