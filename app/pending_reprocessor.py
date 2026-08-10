"""Reprocesamiento local de PDF ya descargados en ``_Pendientes``.

El reprocesador primero clasifica el documento. Solo los candidatos fiscales se
entregan al parser de facturas; los documentos no fiscales con evidencia alta se
archivan en ``_OtrosDocumentos``. Los casos ambiguos permanecen en pendientes.
"""

from collections import Counter
from pathlib import Path

import config
import pdf_reader
import supplier_detector
import supplier_catalog
from suppliers.filename_evidence import detectar_identificador_por_nombre
from suppliers.content_evidence import detectar_identificador_por_contenido

from documents import TipoDocumento, clasificar_documento
from documents.organizer import FOLDERS_BY_TYPE, archivar_otro_documento
from invoices.processor import procesar_factura


ARCHIVED_STATES = {
    TipoDocumento.LISTA_PRECIOS: "lista_archivada",
    TipoDocumento.COMPROBANTE_PAGO: "comprobante_pago_archivado",
    TipoDocumento.ORDEN_PAGO: "orden_pago_archivada",
    TipoDocumento.RRHH_ALTAS_BAJAS: "rrhh_alta_baja_archivada",
    TipoDocumento.RRHH_LIQUIDACIONES: "rrhh_liquidacion_archivada",
    TipoDocumento.RRHH_RECIBOS_LEGAJOS: "rrhh_recibo_legajo_archivado",
    TipoDocumento.RETENCIONES_TRANSFERENCIAS: "retencion_transferencia_archivada",
    TipoDocumento.ESTADO_CUENTA: "estado_cuenta_archivado",
    TipoDocumento.MENUS_CARTAS: "menu_carta_archivado",
    TipoDocumento.INSTRUCTIVO: "instructivo_archivado",
    TipoDocumento.ADMINISTRATIVO: "administrativo_archivado",
    TipoDocumento.COMUNICACION: "comunicacion_archivada",
    TipoDocumento.REMITO_RECIBO: "remito_recibo_archivado",
    TipoDocumento.IMPUESTOS_SERVICIOS: "impuesto_servicio_archivado",
    TipoDocumento.OPERATIVO: "operativo_archivado",
    TipoDocumento.CONSORCIO: "consorcio_archivado",
}


def reprocesar_pendientes() -> list[dict]:
    """Analizar todos los PDF pendientes y devolver un resultado por archivo."""

    carpeta = Path(config.SAVE_FOLDER) / "_Pendientes"
    carpeta.mkdir(parents=True, exist_ok=True)
    resultados = []
    archivos = sorted(carpeta.glob("*.pdf"))
    total = len(archivos)

    for indice, ruta_pdf in enumerate(archivos, start=1):
        # El OCR puede tardar varios segundos en escaneos reales. Mostrar el
        # archivo actual evita confundir trabajo intensivo con una consola
        # congelada y facilita identificar un documento patológico.
        print(f"[{indice}/{total}] Procesando: {ruta_pdf.name}", flush=True)

        try:
            lectura = pdf_reader.leer_pdf(ruta_pdf)
            if lectura.get("ocr_utilizado"):
                metodo = lectura.get("ocr_metodo") or "OCR"
                print(f"    OCR utilizado: {metodo}", flush=True)
            texto = lectura.get("texto_completo", "")

            # Un PDF escaneado sin texto no puede clasificarse con seguridad.
            # En particular, el nombre ``CCF_*.pdf`` no debe bastar para
            # archivarlo como consorcio porque puede contener una factura fiscal.
            if not lectura.get("contiene_texto"):
                resultados.append({
                    "nombre": ruta_pdf.name,
                    "estado": "pendiente",
                    "categoria": "desconocido",
                    "ruta_final": ruta_pdf,
                    "motivo": pdf_reader.describir_fallo_ocr(lectura),
                    "ocr_estado": lectura.get("ocr_estado"),
                })
                continue

            clasificacion = clasificar_documento(texto, ruta_pdf.name)

            if clasificacion.tipo in FOLDERS_BY_TYPE:
                archivo = archivar_otro_documento(
                    ruta_pdf, config.SAVE_FOLDER, clasificacion.tipo
                )
                detalle = clasificacion.motivo
                if archivo.detail:
                    detalle = f"{detalle} {archivo.detail}"
                resultados.append({
                    "nombre": ruta_pdf.name,
                    "estado": ARCHIVED_STATES[clasificacion.tipo],
                    "categoria": clasificacion.tipo.value,
                    "ruta_final": archivo.destination,
                    "motivo": detalle,
                })
                continue

            texto_proveedor = f"{texto}\nNOMBRE ORIGINAL DEL ARCHIVO: {ruta_pdf.name}"
            identificador_nombre = detectar_identificador_por_nombre(ruta_pdf.name)
            if identificador_nombre:
                proveedor_nombre = supplier_catalog.obtener_proveedor_por_identificador(
                    identificador_nombre
                )
                if proveedor_nombre:
                    texto_proveedor += (
                        f"\nEVIDENCIA CANONICA POR NOMBRE: "
                        f"{proveedor_nombre.razon_social}"
                    )

            identificador_contenido = detectar_identificador_por_contenido(texto)
            if identificador_contenido:
                proveedor_contenido = supplier_catalog.obtener_proveedor_por_identificador(
                    identificador_contenido
                )
                if proveedor_contenido:
                    texto_proveedor += (
                        f"\nEVIDENCIA CANONICA POR FIRMA TEXTUAL: "
                        f"{proveedor_contenido.razon_social}"
                    )
            proveedor = supplier_detector.detectar_proveedor(texto_proveedor)
            organizacion = procesar_factura(
                ruta_pdf,
                texto,
                proveedor,
                config.SAVE_FOLDER,
            )
            resultados.append({
                "nombre": ruta_pdf.name,
                "estado": "organizada" if organizacion.organizada else "pendiente",
                "categoria": "factura" if organizacion.organizada else "desconocido",
                "ruta_final": organizacion.ruta_final,
                "motivo": (
                    "El documento contiene evidencia fiscal suficiente."
                    if organizacion.organizada
                    else (organizacion.motivo_pendiente or clasificacion.motivo)
                ),
                "clasificacion": clasificacion,
            })
        except Exception as error:
            resultados.append({
                "nombre": ruta_pdf.name,
                "estado": "error",
                "categoria": "error",
                "ruta_final": ruta_pdf,
                "motivo": str(error),
            })

    return resultados


def mostrar_resumen_reprocesamiento(resultados: list[dict]) -> None:
    """Mostrar detalle por archivo y un resumen agrupado al final."""

    print("\n" + "=" * 50)
    print("REPROCESAMIENTO DE _PENDIENTES")
    print("=" * 50)
    for resultado in resultados:
        print(f"\n{resultado['nombre']}")
        print(f"Estado: {resultado['estado']}")
        print(f"Ruta: {resultado['ruta_final']}")
        if resultado.get("motivo"):
            print(f"Detalle: {resultado['motivo']}")

    counts = Counter(resultado["estado"] for resultado in resultados)
    print("\n" + "=" * 50)
    print("RESUMEN AGRUPADO")
    print("=" * 50)
    if not resultados:
        print("No había documentos pendientes para reprocesar.")
    else:
        labels = {
            "organizada": "Facturas organizadas",
            "pendiente": "Documentos que continúan pendientes",
            "error": "Errores de lectura o procesamiento",
        }
        for state, quantity in sorted(counts.items()):
            label = labels.get(state, state.replace("_", " ").capitalize())
            print(f"{label}: {quantity}")
    print("=" * 50)
