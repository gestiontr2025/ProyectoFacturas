"""Orquestación del análisis y organización de una factura individual."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import invoice_parser
import pdf_reader
import supplier_detector

from documents import TipoDocumento, clasificar_documento
from documents.organizer import archivar_lista_precios
from invoices.filename_builder import construir_nombre_factura
from fiscal.issue_date import detectar_fecha_emision
from invoices.filename_evidence import extraer_evidencia_nombre_archivo
from invoices.validated_file_overrides import get_validated_issue_date
from invoices.organizer import construir_carpeta_final, mover_a_destino_final
from models import FiscalDocument, Supplier

from suppliers.ad_hoc import detectar_emisor_no_recurrente
from suppliers.candidates import registrar_proveedor_ocasional

from invoices.supplier_naming import (
    obtener_nombre_para_carpeta,
    obtener_razon_social_fiscal,
)


@dataclass
class ResultadoOrganizacion:
    """Explicar qué ocurrió con un PDF después de analizarlo."""

    organizada: bool
    ruta_original: Path
    ruta_final: Path
    datos_factura: object
    motivo_pendiente: Optional[str] = None
    tipo_documento: str = "factura"
    documento_fiscal: Optional[FiscalDocument] = None
    proveedor: Optional[Supplier] = None


def _validar_datos_obligatorios(
    documento: FiscalDocument,
    proveedor: Supplier,
) -> list[str]:
    """Enumerar los datos imprescindibles para organizar una factura.

    La validación vive en el modelo de dominio. De esta manera, consola,
    reprocesamiento y futuras interfaces no necesitan mantener listas de
    requisitos diferentes que podrían contradecirse entre sí.
    """
    return documento.missing_required_fields(
        require_supplier=True,
        supplier_present=proveedor.detected,
    )


_CRITICAL_FISCAL_FIELDS = (
    "tipo_comprobante",
    "letra_comprobante",
    "numero_comprobante",
    "fecha_emision",
)


def _completar_campos_faltantes_desde_ocr(datos, datos_ocr) -> bool:
    """Completar solo huecos; nunca pisar evidencia digital ya confiable."""
    changed = False
    fields = _CRITICAL_FISCAL_FIELDS + (
        "cuit_emisor", "cuit_receptor", "moneda", "subtotal", "impuestos",
        "importe_total", "cae", "vencimiento_cae",
    )
    for field in fields:
        if not getattr(datos, field, None) and getattr(datos_ocr, field, None):
            setattr(datos, field, getattr(datos_ocr, field))
            changed = True
    return changed


def _requiere_rescate_semantico(datos, proveedor: Supplier) -> bool:
    """Detectar capas de texto parciales que justifican un segundo OCR."""
    if not proveedor.detected:
        return True
    return any(not getattr(datos, field, None) for field in _CRITICAL_FISCAL_FIELDS)


def _detectar_proveedor_en_texto_rescate(texto_ocr: str, datos_ocr, ruta_pdf: Path) -> dict | None:
    """Intentar catálogo y emisor ocasional sobre una lectura OCR secundaria."""
    if not texto_ocr.strip():
        return None
    texto_proveedor = f"{texto_ocr}\nNOMBRE ORIGINAL DEL ARCHIVO: {ruta_pdf.name}"
    resultado = supplier_detector.detectar_proveedor(texto_proveedor)
    candidato = Supplier.from_detection_result(resultado)
    if candidato.detected:
        return resultado
    return detectar_emisor_no_recurrente(
        texto_ocr,
        getattr(datos_ocr, "cuit_emisor", None),
        ruta_pdf.name,
    )


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

    # Durante esta etapa conservamos ``DatosFactura`` para no romper la API
    # histórica, pero el flujo interno ya dispone de modelos tipados. Este
    # adaptador permite una migración progresiva y comprobable.
    documento = FiscalDocument.from_legacy(datos)
    proveedor = Supplier.from_detection_result(resultado_proveedor)

    # Una compra ocasional no debe incorporarse al catálogo recurrente, pero
    # una factura válida tampoco debe quedar bloqueada. Si el detector normal
    # no encontró proveedor, usamos únicamente firmas inequívocas del
    # encabezado fiscal y construimos una identidad efímera.
    if not proveedor.detected:
        resultado_ocasional = detectar_emisor_no_recurrente(
            texto,
            datos.cuit_emisor,
            ruta_pdf.name,
        )
        if resultado_ocasional is not None:
            resultado_proveedor = resultado_ocasional
            proveedor = Supplier.from_detection_result(resultado_proveedor)

    # El contenido del PDF es la fuente principal. Solo cuando el parser no
    # pudo obtener la letra o el número consultamos el nombre original como
    # evidencia secundaria. Nunca reemplazamos un dato ya detectado dentro de
    # la factura, porque el contenido fiscal tiene mayor autoridad.
    evidencia_nombre = extraer_evidencia_nombre_archivo(ruta_pdf.name)

    # Los métodos siguientes corresponden a nombres generados por sistemas de
    # facturación y contienen de forma explícita tipo, letra, punto de venta y
    # número. Cuando el PDF produce una capa de texto vertical, los detectores
    # genéricos pueden leer falsos positivos; en esos casos la evidencia
    # estructurada del nombre tiene mayor confiabilidad y puede corregirlos.
    metodos_nombre_estructurado = {
        "nombre_con_tipo_letra_y_numero",
        "nombre_fac_compacto",
        "nombre_factura_descriptiva",
        "nombre_fcvta",
        "nombre_nota_descriptiva",
        "nombre_nd_compacto",
        "nombre_con_codigo_afip",
        "nombre_fact_sap_compacto",
    }
    nombre_es_estructurado = evidencia_nombre.metodo in metodos_nombre_estructurado

    if evidencia_nombre.tipo_comprobante and (
        nombre_es_estructurado or not datos.tipo_comprobante
    ):
        datos.tipo_comprobante = evidencia_nombre.tipo_comprobante

    if evidencia_nombre.letra_comprobante and (
        nombre_es_estructurado or not datos.letra_comprobante
    ):
        datos.letra_comprobante = evidencia_nombre.letra_comprobante

    if evidencia_nombre.numero_comprobante and (
        nombre_es_estructurado or not datos.numero_comprobante
    ):
        datos.numero_comprobante = evidencia_nombre.numero_comprobante

    # Algunos sistemas dibujan el encabezado como imagen. El texto extraído
    # conserva la fecha, pero pierde la palabra FACTURA. Si el nombre ya aportó
    # tipo, letra y número de manera inequívoca, habilitamos un último respaldo
    # para recuperar la primera fecha válida del contenido.
    if (
        not datos.fecha_emision
        and datos.tipo_comprobante
        and datos.letra_comprobante
        and datos.numero_comprobante
    ):
        datos.fecha_emision = detectar_fecha_emision(
            texto,
            contexto_fiscal_confirmado=True,
        )

    # Una capa de texto vertical puede conservar únicamente el vencimiento y
    # perder la etiqueta de emisión. Las excepciones verificadas manualmente
    # tienen prioridad sobre una fecha secundaria extraída automáticamente.
    fecha_validada = get_validated_issue_date(ruta_pdf.name)
    if fecha_validada:
        datos.fecha_emision = fecha_validada

    # OCR es un rescate de último recurso, no la ruta normal. Antes de llegar
    # aquí ya agotamos parser digital, proveedor por texto/nombre, evidencia
    # estructurada del filename y detección semántica de fecha. Solo si todavía
    # falta proveedor o un dato fiscal crítico hacemos una segunda lectura OCR.
    # Nunca reemplazamos evidencia digital ya confiable.
    if _requiere_rescate_semantico(datos, proveedor):
        try:
            rescate = pdf_reader.extraer_texto_ocr_forzado(ruta_pdf)
        except Exception:
            rescate = {"texto_completo": "", "estado": "ocr_error"}
        texto_ocr = rescate.get("texto_completo", "") or ""
        if texto_ocr.strip():
            parseo_ocr = invoice_parser.extraer_datos_factura(texto_ocr)
            datos_ocr = parseo_ocr.datos
            _completar_campos_faltantes_desde_ocr(datos, datos_ocr)

            if not proveedor.detected:
                resultado_rescate = _detectar_proveedor_en_texto_rescate(
                    texto_ocr, datos_ocr, ruta_pdf
                )
                if resultado_rescate is None:
                    # A veces una fuente conserva el CUIT y la otra el nombre.
                    # La fusión se reserva exclusivamente a identidad del emisor.
                    resultado_rescate = detectar_emisor_no_recurrente(
                        f"{texto}\n{texto_ocr}",
                        datos.cuit_emisor or datos_ocr.cuit_emisor,
                        ruta_pdf.name,
                    )
                if resultado_rescate is not None:
                    resultado_proveedor = resultado_rescate
                    proveedor = Supplier.from_detection_result(resultado_proveedor)

    # La evidencia del nombre puede completar campos del objeto histórico.
    # Reconstruimos el modelo para que refleje esos cambios antes de validar.
    documento = FiscalDocument.from_legacy(datos)
    faltantes = _validar_datos_obligatorios(documento, proveedor)

    if faltantes:
        return ResultadoOrganizacion(
            organizada=False,
            ruta_original=ruta_pdf,
            ruta_final=ruta_pdf,
            datos_factura=datos,
            motivo_pendiente="Faltan: " + ", ".join(faltantes),
            documento_fiscal=documento,
            proveedor=proveedor,
        )

    # La razón social fiscal se conserva dentro del nombre del archivo. Para
    # la carpeta preferimos el nombre de fantasía cuando existe: es más breve
    # y reconocible para el usuario (por ejemplo, ``Colppy``).
    razon_social = obtener_razon_social_fiscal(resultado_proveedor)
    nombre_carpeta = obtener_nombre_para_carpeta(resultado_proveedor)
    nombre_final = construir_nombre_factura(datos, razon_social)
    carpeta_final = construir_carpeta_final(
        carpeta_raiz, nombre_carpeta, datos.fecha_emision
    )
    ruta_final = mover_a_destino_final(ruta_pdf, carpeta_final, nombre_final)

    # Los emisores ocasionales se registran en un archivo auxiliar separado del
    # catálogo canónico. El identificador fiscal evita contar dos veces el
    # mismo comprobante si se vuelve a ejecutar el reprocesamiento.
    if proveedor.detection_method in {
        "encabezado_fiscal_no_persistente",
        "encabezado_fiscal_generico_no_persistente",
        "nombre_archivo_validado_no_persistente",
    } and proveedor.cuit:
        document_key = "|".join(
            value or ""
            for value in (
                documento.issue_date,
                documento.document_type,
                documento.fiscal_letter,
                documento.document_number,
            )
        )
        registrar_proveedor_ocasional(
            cuit=proveedor.cuit,
            business_name=proveedor.legal_name or proveedor.display_name or "PROVEEDOR OCASIONAL",
            document_key=document_key,
            folder_name=nombre_carpeta,
        )

    return ResultadoOrganizacion(
        organizada=True,
        ruta_original=ruta_pdf,
        ruta_final=ruta_final,
        datos_factura=datos,
        documento_fiscal=documento,
        proveedor=proveedor,
    )
