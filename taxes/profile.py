"""Construcción del perfil impositivo acumulado por proveedor."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable

import business_config
import invoice_parser
import pdf_reader
import supplier_detector
from suppliers.ad_hoc import detectar_emisor_no_recurrente
from invoices.filename_evidence import extraer_evidencia_nombre_archivo
from taxes.extractor import TaxEvidence, extract_tax_evidence


@dataclass
class SupplierTaxProfile:
    """Acumular los conceptos observados en todas las facturas de un CUIT."""

    supplier_name: str
    supplier_cuit: str
    vat_27: bool = False
    vat_21: bool = False
    vat_10_5: bool = False
    vat_perception: bool = False
    iibb_caba_perception: bool = False
    iibb_bsas_perception: bool = False
    internal_taxes: bool = False
    invoices_analyzed: int = 0

    def merge(self, evidence: TaxEvidence) -> None:
        self.vat_27 = self.vat_27 or evidence.vat_27
        self.vat_21 = self.vat_21 or evidence.vat_21
        self.vat_10_5 = self.vat_10_5 or evidence.vat_10_5
        self.vat_perception = self.vat_perception or evidence.vat_perception
        self.iibb_caba_perception = self.iibb_caba_perception or evidence.iibb_caba_perception
        self.iibb_bsas_perception = self.iibb_bsas_perception or evidence.iibb_bsas_perception
        self.internal_taxes = self.internal_taxes or evidence.internal_taxes
        self.invoices_analyzed += 1


def _iter_organized_pdfs(root: Path) -> Iterable[Path]:
    if not root.exists():
        return ()
    return (
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.suffix.lower() == ".pdf"
        and not any(part.startswith("_") for part in path.relative_to(root).parts)
    )


def _format_cuit(value: object) -> str:
    digits = re.sub(r"\D", "", str(value or ""))
    if len(digits) != 11:
        return ""
    return f"{digits[:2]}-{digits[2:10]}-{digits[10]}"


def _name_from_organized_filename(path: Path) -> str:
    stem = path.stem
    marker = "_MADERO_ROOF_TOP_"
    if marker in stem:
        return stem.split(marker, 1)[1].replace("_", " ").strip()
    return path.parent.parent.parent.name.replace("_", " ").strip()


def _resolve_supplier(text: str, path: Path, parsed_data: object) -> tuple[str, str] | None:
    detection_text = f"{text}\nNOMBRE ORGANIZADO: {path.name}"
    result = supplier_detector.detectar_proveedor(detection_text)

    if not result.get("proveedor_detectado"):
        result = detectar_emisor_no_recurrente(
            text,
            getattr(parsed_data, "cuit_emisor", None),
            path.name,
        ) or {}

    if result.get("proveedor_detectado"):
        name = (
            result.get("razon_social_canonica")
            or result.get("razon_social_encontrada")
            or result.get("nombre_proveedor")
        )
        cuit = _format_cuit(result.get("cuit_canonico") or result.get("cuit_encontrado"))
        if name and cuit:
            return str(name).strip(), cuit

    # Respaldo para proveedores ocasionales ya organizados: usamos el nombre
    # canónico grabado en el archivo y elegimos un CUIT diferente al receptor.
    candidate_cuits = invoice_parser.extraer_cuits_en_orden(text)
    issuer_cuit = next(
        (
            _format_cuit(candidate)
            for candidate in candidate_cuits
            if _format_cuit(candidate)
            and not business_config.es_cuit_receptor(candidate)
        ),
        "",
    )
    fallback_name = _name_from_organized_filename(path)
    if fallback_name and issuer_cuit:
        return fallback_name, issuer_cuit
    return None


def build_supplier_tax_profiles(root: Path) -> tuple[list[SupplierTaxProfile], int, int]:
    """Analizar facturas organizadas y devolver perfiles únicos por CUIT.

    Retorna ``(perfiles, pdf_analizados, pdf_omitidos)``. Un documento se omite
    cuando no puede leerse, no parece un comprobante fiscal o no se identifica
    de forma segura al emisor.
    """
    profiles: dict[str, SupplierTaxProfile] = {}
    analyzed = 0
    skipped = 0

    for path in _iter_organized_pdfs(Path(root)):
        try:
            reading = pdf_reader.leer_pdf(path)
            text = reading.get("texto_completo", "")
            if not text.strip():
                skipped += 1
                continue
            parsed = invoice_parser.extraer_datos_factura(text).datos
            filename_evidence = extraer_evidencia_nombre_archivo(path.name)
            organized_match = re.search(
                r"(?:^|\d{2}-\d{2})(?:FC|NC|ND)[ABC](\d{5})-(\d{8})",
                path.stem.upper(),
            )
            document_type = parsed.tipo_comprobante or filename_evidence.tipo_comprobante
            document_number = parsed.numero_comprobante or filename_evidence.numero_comprobante
            if organized_match and not document_number:
                document_number = f"{organized_match.group(1)}-{organized_match.group(2)}"
            if organized_match and not document_type:
                document_type = "FACTURA"
            if not document_type or not document_number:
                skipped += 1
                continue
            supplier = _resolve_supplier(text, path, parsed)
            if supplier is None:
                skipped += 1
                continue
            name, cuit = supplier
            profile = profiles.setdefault(
                re.sub(r"\D", "", cuit),
                SupplierTaxProfile(supplier_name=name, supplier_cuit=cuit),
            )
            # Preferimos el nombre más descriptivo si diferentes documentos
            # aportan razón social y nombre simplificado para el mismo CUIT.
            if len(name) > len(profile.supplier_name):
                profile.supplier_name = name
            profile.merge(extract_tax_evidence(text))
            analyzed += 1
        except Exception:
            # La exportación es una tarea de diagnóstico: un PDF problemático
            # no debe impedir generar el perfil del resto de los proveedores.
            skipped += 1

    ordered = sorted(profiles.values(), key=lambda item: item.supplier_name.upper())
    return ordered, analyzed, skipped
