"""Auditoría precisa y no destructiva de fechas en facturas organizadas.

La auditoría usa exclusivamente texto digital y un detector con candidatos,
puntuación y confianza. Solo propone/mueve cuando la evidencia de fecha de
emisión es alta; los casos ambiguos se informan para revisión manual.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import shutil

import pdf_reader
from fiscal.issue_date import (
    DateAuditAnalysis,
    DateAuditCandidate,
    analizar_fecha_emision_para_auditoria,
    resolver_candidatos_fecha,
)
from fiscal.issue_date_geometry import extract_geometry_date_candidates


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


def _candidate_summary(candidates) -> str:
    if not candidates:
        return "sin candidatos"

    rendered = []
    for candidate in candidates[:4]:
        rendered.append(
            f"{candidate.issue_date} (score {candidate.score}: {candidate.reason})"
        )
    return " | ".join(rendered)


def _merge_analysis_with_geometry(
    textual: DateAuditAnalysis,
    geometry_candidates,
    *,
    current_date: str,
) -> DateAuditAnalysis:
    """Unir evidencia textual y geométrica y resolverla con una sola política.

    La geometría NO es un segundo parser ni decide por su cuenta. Solo aporta
    candidatos al mismo motor de decisión definido en ``fiscal.issue_date``.
    Así evitamos que parser textual, geometría y auditoría tengan reglas
    incompatibles para el mismo comprobante.
    """

    geometry_as_text = tuple(
        DateAuditCandidate(
            issue_date=c.issue_date,
            score=c.score,
            reason=c.reason,
            position=10_000_000 + (c.page * 100_000) + int(c.y * 10),
        )
        for c in geometry_candidates
    )

    return resolver_candidatos_fecha(
        tuple(textual.candidates) + geometry_as_text,
        fecha_actual=current_date,
    )



def audit_organized_invoice_dates(
    root: str | Path,
    *,
    apply: bool = False,
    allow_ocr: bool = False,
    include_verified: bool = False,
) -> list[InvoiceDateAuditResult]:
    """Auditar fechas organizadas y mover solo con confianza alta.

    Reglas de seguridad:
    - La pasada normal usa exclusivamente texto digital.
    - OCR solo se activa de forma explícita con ``allow_ocr=True`` y únicamente
      para archivos que no poseen texto digital utilizable.
    - La fecha actual del nombre es una señal, no una verdad absoluta.
    - Vencimientos, CAE, período facturado e inicio de actividad no pueden
      justificar un movimiento.
    - Un caso ambiguo se informa como ``manual_review`` y nunca se mueve.
    - Solo ``confidence == high`` puede generar ``would_move/date_repaired``.
    """

    root = Path(root)
    results: list[InvoiceDateAuditResult] = []

    for source in sorted(root.glob("*/*/*/*.pdf")):
        try:
            relative = source.relative_to(root)
        except ValueError:
            continue

        if relative.parts[0].startswith("_"):
            continue

        match = _STANDARD_FILENAME.match(source.name)
        if match is None:
            continue

        try:
            text = pdf_reader.leer_pdf(
                source,
                permitir_ocr=False,
            ).get("texto_completo", "")

            used_ocr = False
            if not text.strip():
                if not allow_ocr:
                    results.append(
                        InvoiceDateAuditResult(
                            status="skipped_no_digital_text",
                            source=source,
                            detail=(
                                "El PDF no tiene texto digital utilizable. "
                                "La auditoría rápida no activa OCR. Podés revisar "
                                "solo estos casos con --audit-organized-dates --ocr."
                            ),
                        )
                    )
                    continue

                # OCR selectivo: únicamente llegamos aquí cuando la extracción
                # digital no produjo ningún texto. Nunca se OCRiza un PDF que
                # ya pudo analizarse con el parser normal.
                ocr_result = pdf_reader.extraer_texto_ocr_forzado(source)
                text = (ocr_result or {}).get("texto_completo", "")
                if not text.strip():
                    results.append(
                        InvoiceDateAuditResult(
                            status="ocr_unresolved",
                            source=source,
                            detail=(
                                "El PDF no tiene texto digital y el OCR selectivo "
                                "no recuperó una fecha auditable. "
                                f"Estado OCR: {(ocr_result or {}).get('estado')}. "
                                f"Detalle: {(ocr_result or {}).get('error') or 'sin detalle'}."
                            ),
                        )
                    )
                    continue
                used_ocr = True

            if len(relative.parts) < 4:
                continue

            current_year = relative.parts[1]
            current_date = (
                f"{match.group('day')}/{match.group('month')}/{current_year}"
            )

            textual_analysis = analizar_fecha_emision_para_auditoria(
                text,
                fecha_actual=current_date,
            )

            # Segunda lectura digital, todavía sin OCR: PyMuPDF conserva las
            # coordenadas visuales de las palabras. Esto permite distinguir
            # fecha de emisión y vencimiento cuando pypdf aplana columnas en un
            # orden engañoso. Se ejecuta sobre todos los PDF digitales porque
            # es rápida y funciona como verificación independiente.
            geometry_candidates = extract_geometry_date_candidates(source)
            analysis = _merge_analysis_with_geometry(
                textual_analysis,
                geometry_candidates,
                current_date=current_date,
            )

            # Si el motor no puede decidir con seguridad, lo informa en vez de
            # inventar una corrección. Esto es especialmente importante para
            # layouts ARCA donde la extracción PDF puede reordenar columnas.
            if analysis.confidence == "ambiguous":
                results.append(
                    InvoiceDateAuditResult(
                        status="manual_review",
                        source=source,
                        detail=(
                            f"Fecha actual {current_date}. {analysis.reason} "
                            f"Candidatos: {_candidate_summary(analysis.candidates)}"
                        ),
                    )
                )
                continue

            if analysis.issue_date is None:
                # Fechas futuras se distinguen porque históricamente fueron una
                # señal clara de confusión con vencimientos. Nunca se mueven.
                if analysis.candidates and "fechas futuras" in analysis.reason.lower():
                    results.append(
                        InvoiceDateAuditResult(
                            status="blocked_future_date",
                            source=source,
                            detail=(
                                f"Fecha actual {current_date}. {analysis.reason} "
                                f"Candidatos: {_candidate_summary(analysis.candidates)}"
                            ),
                        )
                    )
                elif analysis.candidates:
                    results.append(
                        InvoiceDateAuditResult(
                            status="manual_review",
                            source=source,
                            detail=(
                                f"Fecha actual {current_date}. {analysis.reason} "
                                f"Candidatos: {_candidate_summary(analysis.candidates)}"
                            ),
                        )
                    )
                else:
                    # Antes estos archivos desaparecían silenciosamente del
                    # informe. Eso hacía que el resumen pareciera haber
                    # auditado todo cuando en realidad una parte no tenía
                    # evidencia suficiente. Ahora quedan contabilizados sin
                    # generar una falsa alarma de revisión manual.
                    results.append(
                        InvoiceDateAuditResult(
                            status="unresolved_date",
                            source=source,
                            detail=(
                                f"Fecha actual {current_date}. {analysis.reason} "
                                "No se realizó ningún cambio."
                            ),
                        )
                    )
                continue

            issue_date = analysis.issue_date

            # Construimos SIEMPRE la ruta canónica antes de decidir si el
            # archivo ya está correcto. La fecha del nombre y la carpeta
            # año/mes son dos piezas independientes: una auditoría anterior o
            # una corrección manual puede haber arreglado solo una de ellas.
            #
            # Ejemplos que esta comprobación corrige:
            # - carpeta correcta + nombre con día/mes viejo;
            # - nombre correcto + carpeta año/mes equivocada;
            # - ambos incorrectos.
            destination = build_corrected_path(root, source, issue_date)
            if destination is None:
                results.append(
                    InvoiceDateAuditResult(
                        status="manual_review",
                        source=source,
                        detail=(
                            f"Se detectó fecha de emisión {issue_date}, pero no "
                            "se pudo construir una ruta canónica segura a partir "
                            "del nombre actual."
                        ),
                    )
                )
                continue

            # Solo consideramos el archivo completamente correcto cuando tanto
            # el nombre como la carpeta coinciden con la ruta canónica.
            if destination == source:
                if include_verified:
                    results.append(
                        InvoiceDateAuditResult(
                            status="verified_ok",
                            source=source,
                            destination=source,
                            detail=(
                                f"Fecha {issue_date} verificada. "
                                f"Evidencia: {analysis.reason}."
                            ),
                        )
                    )
                continue

            # Una reparación automática requiere confianza alta. ``stable`` se
            # usa exclusivamente para confirmar la fecha ya existente.
            if analysis.confidence != "high":
                results.append(
                    InvoiceDateAuditResult(
                        status="manual_review",
                        source=source,
                        detail=(
                            f"Fecha actual {current_date}; candidato {issue_date}. "
                            f"Confianza {analysis.confidence}: {analysis.reason}."
                        ),
                    )
                )
                continue

            # Cuando la evidencia proviene de OCR exigimos además un candidato
            # ganador prácticamente inequívoco. El OCR es útil para escaneos,
            # pero una lectura secundaria nunca debe tener el mismo umbral que
            # el texto digital original en una operación destructiva.
            if used_ocr:
                winner = next(
                    (c for c in analysis.candidates if c.issue_date == issue_date),
                    None,
                )
                if winner is None or winner.score < 96:
                    results.append(
                        InvoiceDateAuditResult(
                            status="manual_review_ocr",
                            source=source,
                            detail=(
                                f"OCR detectó {issue_date}, pero la evidencia no "
                                "alcanza el umbral reforzado para mover automáticamente. "
                                f"Candidatos: {_candidate_summary(analysis.candidates)}"
                            ),
                        )
                    )
                    continue

            if destination.exists():
                results.append(
                    InvoiceDateAuditResult(
                        status="conflict",
                        source=source,
                        destination=destination,
                        detail=(
                            "El destino corregido ya existe; no se realizó "
                            "ningún cambio."
                        ),
                    )
                )
                continue

            current_location = f"{relative.parts[1]}/{relative.parts[2]} - {source.name}"
            expected_relative = destination.relative_to(root)
            expected_location = (
                f"{expected_relative.parts[1]}/{expected_relative.parts[2]} - "
                f"{destination.name}"
            )
            detail = (
                f"Fecha de emisión {issue_date} con confianza alta. "
                f"Evidencia: {analysis.reason}. "
                f"Ubicación actual: {current_location}. "
                f"Ubicación canónica: {expected_location}."
                + (" Fuente: OCR selectivo." if used_ocr else " Fuente: texto digital.")
            )

            if not apply:
                results.append(
                    InvoiceDateAuditResult(
                        status="would_move_ocr" if used_ocr else "would_move",
                        source=source,
                        destination=destination,
                        detail=f"Vista previa: {detail}",
                    )
                )
                continue

            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(destination))
            results.append(
                InvoiceDateAuditResult(
                    status="date_repaired_ocr" if used_ocr else "date_repaired",
                    source=source,
                    destination=destination,
                    detail=f"Archivo reubicado. {detail}",
                )
            )

        except Exception as error:
            # Una factura problemática nunca debe interrumpir todo el lote.
            results.append(
                InvoiceDateAuditResult(
                    status="error",
                    source=source,
                    detail=str(error),
                )
            )

    return results
