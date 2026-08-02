"""Pruebas del catálogo JSON y de su criterio de recurrencia."""

import json
from pathlib import Path

import supplier_catalog


CATALOG_PATH = Path(__file__).resolve().parents[1] / "suppliers" / "data" / "supplier_catalog.json"


def test_catalog_json_contains_each_supplier_once():
    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    suppliers = data["suppliers"]
    identifiers = [item["identifier"] for item in suppliers]
    cuits = [item["cuit"] for item in suppliers]
    assert len(identifiers) == len(set(identifiers))
    assert len(cuits) == len(set(cuits))


def test_catalog_excludes_single_occurrence_emitters():
    for supplier in supplier_catalog.listar_proveedores():
        assert supplier.cantidad_comprobantes_observados >= 2


def test_catalog_was_generated_with_requested_threshold():
    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    assert data["source"]["minimum_occurrences"] == 2
    assert data["source"]["included_suppliers"] == 114


def test_compatibility_lookup_function_exists():
    supplier = supplier_catalog.obtener_proveedor_por_identificador("arta_verduleros")
    assert supplier is not None
    assert supplier.cuit == "30-71867492-8"


def test_excel_corrected_historical_cuit_for_chesko():
    supplier = supplier_catalog.obtener_proveedor("chesko_agustin_ezequiel")
    assert supplier is not None
    assert supplier.cuit == "20-37018937-5"
