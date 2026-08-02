"""Orquestación del análisis y organización de una factura individual."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import invoice_parser

from documents import TipoDocumento, clasificar_documento
from documents.organizer import archivar_lista_precios
from invoices.filename_builder import construir_nombre_factura
from invoices.filename_evidence import extraer_evidencia_nombre_archivo
from invoices.organizer import construir_carpeta_final, mover_a_destino_final


@dataclass
class ResultadoOrganizacion:
    """Explicar qué ocurrió con un PDF después de analizarlo."""

    organizada: bool
    ruta_original: Path
    ruta_final: Path
    datos_factura: object
    motivo_pendiente: Optional[str] = None
    tipo_documento: str = "factura"


def _validar_datos_obligatorios(datos, resultado_proveedor: dict) -> list[str]:
    """Enumerar los datos imprescindibles para nombrar y archivar la factura."""
    faltantes = []
    if not datos.fecha_emision:
        faltantes.append("fecha de emisión")
    if not datos.tipo_comprobante:
        faltantes.append("tipo de comprobante")
    if not datos.letra_comprobante:
        faltantes.append("letra del comprobante")
    if not datos.numero_comprobante:
        faltantes.append("número de comprobante")
    if not resultado_proveedor or not resultado_proveedor.get("proveedor_detectado"):
        faltantes.append("proveedor")
    return faltantes


def procesar_factura(ruta_pdf, texto: str, resultado_proveedor: dict, carpeta_raiz) -> ResultadoOrganizacion:
    """Interpretar un PDF y moverlo solamente cuando los datos son confiables.

    Un documento incompleto permanece en ``_Pendientes``. Esta decisión es
    deliberada: una clasificación imperfecta nunca debe hacer desaparecer una
    factura ni colocarla bajo el proveedor equivocado.
    """
    ruta_pdf = Path(ruta_pdf)

    # Clasificamos antes de ejecutar el parser fiscal. Una lista de precios no
    # es una factura defectuosa: es otro tipo de documento y debe seguir una
    # ruta distinta. Esto mantiene ``_Pendientes`` reservado para casos que sí
    # requieren revisión.
    clasificacion = clasificar_documento(texto, ruta_pdf.name)
    if clasificacion.tipo is TipoDocumento.LISTA_PRECIOS:
        ruta_final = archivar_lista_precios(ruta_pdf, carpeta_raiz)
        return ResultadoOrganizacion(
            organizada=False,
            ruta_original=ruta_pdf,
            ruta_final=ruta_final,
            datos_factura=None,
            motivo_pendiente=clasificacion.motivo,
            tipo_documento="lista_de_precios",
        )

    parseo = invoice_parser.extraer_datos_factura(texto)
    datos = parseo.datos

    # El contenido del PDF es la fuente principal. Solo cuando el parser no
    # pudo obtener la letra o el número consultamos el nombre original como
    # evidencia secundaria. Nunca reemplazamos un dato ya detectado dentro de
    # la factura, porque el contenido fiscal tiene mayor autoridad.
    evidencia_nombre = extraer_evidencia_nombre_archivo(ruta_pdf.name)

    if not datos.tipo_comprobante and evidencia_nombre.tipo_comprobante:
        datos.tipo_comprobante = evidencia_nombre.tipo_comprobante

    if not datos.letra_comprobante and evidencia_nombre.letra_comprobante:
        datos.letra_comprobante = evidencia_nombre.letra_comprobante

    if not datos.numero_comprobante and evidencia_nombre.numero_comprobante:
        datos.numero_comprobante = evidencia_nombre.numero_comprobante

    faltantes = _validar_datos_obligatorios(datos, resultado_proveedor)

    if faltantes:
        return ResultadoOrganizacion(
            organizada=False,
            ruta_original=ruta_pdf,
            ruta_final=ruta_pdf,
            datos_factura=datos,
            motivo_pendiente="Faltan: " + ", ".join(faltantes),
        )

    razon_social = resultado_proveedor["razon_social_encontrada"]
    nombre_final = construir_nombre_factura(datos, razon_social)
    carpeta_final = construir_carpeta_final(
        carpeta_raiz, razon_social, datos.fecha_emision
    )
    ruta_final = mover_a_destino_final(ruta_pdf, carpeta_final, nombre_final)

    return ResultadoOrganizacion(
        organizada=True,
        ruta_original=ruta_pdf,
        ruta_final=ruta_final,
        datos_factura=datos,
    )
