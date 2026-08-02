"""Auditoría y reparación segura de fechas en facturas ya organizadas.

El comando trabaja primero en vista previa. Solo mueve un archivo cuando:

- su nombre sigue el formato estándar del proyecto;
- el PDF contiene una fecha de emisión válida;
- la fecha detectada difiere de la fecha usada en la ruta;
- el destino corregido no existe.

Esta herramienta permite reparar regresiones históricas sin borrar archivos ni
volver a descargar correos.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import re

import invoice_parser
import pdf_reader


_STANDARD_FILENAME = re.compile(
    r"^(?P<day>\d{2})-(?P<month>\d{2})(?P<rest>(?:FC|NC|ND)[ABC].+\.PDF)$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class InvoiceDateAuditResult:
    status: str
    source: Path
    destination: Path | None = None
    detail: str | None = None


def build_corrected_path(root: Path, source: Path, issue_date: str) -> Path | None:
    """Construir la ruta corregida sin modificar el sistema de archivos."""

    match = _STANDARD_FILENAME.match(source.name)
    if not match:
        return None

    try:
        day, month, year = issue_date.split("/")
        int(day), int(month), int(year)
    except (ValueError, AttributeError):
        return None

    try:
        relative = source.relative_to(root)
    except ValueError:
        return None
    if len(relative.parts) < 4 or relative.parts[0].startswith("_"):
        return None

    supplier_folder = relative.parts[0]
    filename = f"{day.zfill(2)}-{month.zfill(2)}{match.group('rest')}"
    return root / supplier_folder / year / month.zfill(2) / filename


def audit_organized_invoice_dates(root: str | Path, *, apply: bool = False) -> list[InvoiceDateAuditResult]:
    """Detectar fechas de carpeta/nombre inconsistentes y, opcionalmente, repararlas."""

    root = Path(root)
    results: list[InvoiceDateAuditResult] = []

    for source in sorted(root.glob("*/*/*/*.pdf")):
        if source.relative_to(root).parts[0].startswith("_"):
            continue
        if not _STANDARD_FILENAME.match(source.name):
            continue

        try:
            text = pdf_reader.leer_pdf(source).get("texto_completo", "")
            parsed = invoice_parser.extraer_datos_factura(text).datos
            if not parsed.fecha_emision:
                continue
            destination = build_corrected_path(root, source, parsed.fecha_emision)
            if destination is None or destination == source:
                continue

            if destination.exists():
                results.append(InvoiceDateAuditResult(
                    status="conflict",
                    source=source,
                    destination=destination,
                    detail="El destino corregido ya existe; no se realizó ningún cambio.",
                ))
                continue

            if not apply:
                results.append(InvoiceDateAuditResult(
                    status="would_move",
                    source=source,
                    destination=destination,
                    detail=f"Vista previa: fecha de emisión detectada {parsed.fecha_emision}.",
                ))
                continue

            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(destination))
            results.append(InvoiceDateAuditResult(
                status="date_repaired",
                source=source,
                destination=destination,
                detail=f"Archivo reubicado según la fecha de emisión {parsed.fecha_emision}.",
            ))
        except Exception as error:  # La auditoría nunca debe interrumpir el lote completo.
            results.append(InvoiceDateAuditResult(
                status="error",
                source=source,
                detail=str(error),
            ))

    return results
