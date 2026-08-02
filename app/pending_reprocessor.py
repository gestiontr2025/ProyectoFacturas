"""Reprocesamiento local de PDF ya descargados en ``_Pendientes``.

Este modo evita volver a consultar Gmail cada vez que se mejora el parser. Es
especialmente útil durante el desarrollo y también para recuperar documentos
que antes no pudieron clasificarse.
"""

from pathlib import Path

import config
import pdf_reader
import supplier_detector

from documents import TipoDocumento, clasificar_documento
from documents.organizer import archivar_otro_documento
from invoices.processor import procesar_factura


def reprocesar_pendientes() -> list[dict]:
    """Analizar todos los PDF pendientes y devolver un resultado por archivo."""

    carpeta = Path(config.SAVE_FOLDER) / "_Pendientes"
    carpeta.mkdir(parents=True, exist_ok=True)
    resultados = []

    for ruta_pdf in sorted(carpeta.glob("*.pdf")):
        try:
            lectura = pdf_reader.leer_pdf(ruta_pdf)
            texto = lectura.get("texto_completo", "")
            clasificacion = clasificar_documento(texto, ruta_pdf.name)

            if clasificacion.tipo in {
                TipoDocumento.LISTA_PRECIOS,
                TipoDocumento.COMPROBANTE_PAGO,
                TipoDocumento.ORDEN_PAGO,
            }:
                archivo = archivar_otro_documento(
                    ruta_pdf, config.SAVE_FOLDER, clasificacion.tipo
                )
                estados = {
                    TipoDocumento.LISTA_PRECIOS: "lista_archivada",
                    TipoDocumento.COMPROBANTE_PAGO: "comprobante_pago_archivado",
                    TipoDocumento.ORDEN_PAGO: "orden_pago_archivada",
                }
                detalle = clasificacion.motivo
                if archivo.detail:
                    detalle = f"{detalle} {archivo.detail}"
                resultados.append({
                    "nombre": ruta_pdf.name,
                    "estado": estados[clasificacion.tipo],
                    "ruta_final": archivo.destination,
                    "motivo": detalle,
                })
                continue

            texto_proveedor = f"{texto}\nNOMBRE ORIGINAL DEL ARCHIVO: {ruta_pdf.name}"
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
                "ruta_final": organizacion.ruta_final,
                "motivo": organizacion.motivo_pendiente,
            })
        except Exception as error:
            resultados.append({
                "nombre": ruta_pdf.name,
                "estado": "error",
                "ruta_final": ruta_pdf,
                "motivo": str(error),
            })

    return resultados


def mostrar_resumen_reprocesamiento(resultados: list[dict]) -> None:
    """Mostrar un resumen breve pensado para diagnosticar el flujo."""

    print("\n" + "=" * 50)
    print("REPROCESAMIENTO DE _PENDIENTES")
    print("=" * 50)
    for resultado in resultados:
        print(f"\n{resultado['nombre']}")
        print(f"Estado: {resultado['estado']}")
        print(f"Ruta: {resultado['ruta_final']}")
        if resultado.get("motivo"):
            print(f"Detalle: {resultado['motivo']}")
    print("\n" + "=" * 50)
