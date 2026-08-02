from pathlib import Path

from openpyxl import load_workbook

from taxes.exporter import HEADERS, export_supplier_tax_profile
from taxes.extractor import extract_tax_evidence
from taxes.profile import SupplierTaxProfile


def test_extracts_all_requested_tax_categories():
    text = """
    IVA 27%: 100
    IVA 21,00 %: 200
    I.V.A. 10,5%: 50
    Percepción IVA: 5
    PERCEP. I.B. CAP. 3,00%
    Percepción IIBB Buenos Aires 2%
    Impuestos Internos 25%
    """
    evidence = extract_tax_evidence(text)
    assert evidence.vat_27
    assert evidence.vat_21
    assert evidence.vat_10_5
    assert evidence.vat_perception
    assert evidence.iibb_caba_perception
    assert evidence.iibb_bsas_perception
    assert evidence.internal_taxes


def test_profile_accumulates_rates_from_different_invoices():
    profile = SupplierTaxProfile("Proveedor", "30-12345678-9")
    profile.merge(extract_tax_evidence("IVA 21%: 100"))
    profile.merge(extract_tax_evidence("IVA 10,5%: 50"))
    assert profile.vat_21 is True
    assert profile.vat_10_5 is True
    assert profile.invoices_analyzed == 2


def test_export_writes_requested_columns(monkeypatch, tmp_path):
    profile = SupplierTaxProfile(
        supplier_name="PROVEEDOR DE PRUEBA SRL",
        supplier_cuit="30-12345678-9",
        vat_21=True,
        vat_10_5=True,
        iibb_caba_perception=True,
    )
    monkeypatch.setattr(
        "taxes.exporter.build_supplier_tax_profiles",
        lambda root: ([profile], 2, 0),
    )
    output = tmp_path / "perfil.xlsx"
    result = export_supplier_tax_profile(tmp_path, output)

    workbook = load_workbook(result.output_path)
    sheet = workbook["Perfil impositivo"]
    assert tuple(cell.value for cell in sheet[1]) == HEADERS
    assert sheet["A2"].value == "PROVEEDOR DE PRUEBA SRL"
    assert sheet["D2"].value == "Sí"
    assert sheet["E2"].value == "Sí"
    assert sheet["G2"].value == "Sí"
    assert sheet["C2"].value == "No"
