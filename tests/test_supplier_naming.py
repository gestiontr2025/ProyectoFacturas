"""Pruebas de nombres legales y comerciales usados por el organizador."""

from invoices.supplier_naming import (
    obtener_nombre_para_carpeta,
    obtener_razon_social_fiscal,
)


def test_colppy_usa_nombre_de_fantasia_para_la_carpeta():
    proveedor = {
        "razon_social_encontrada": "ALL ONLINE SOLUTIONS S. A. U.",
        "nombre_fantasia": "Colppy",
    }

    assert obtener_nombre_para_carpeta(proveedor) == "Colppy"
    assert obtener_razon_social_fiscal(proveedor) == "ALL ONLINE SOLUTIONS S. A. U."


def test_sin_nombre_de_fantasia_se_usa_razon_social():
    proveedor = {
        "razon_social_encontrada": "CHESKO AGUSTIN EZEQUIEL",
        "nombre_fantasia": None,
    }

    assert obtener_nombre_para_carpeta(proveedor) == "CHESKO AGUSTIN EZEQUIEL"
