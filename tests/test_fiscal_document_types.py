"""Pruebas del motor fiscal para las nueve combinaciones prioritarias.

Cada caso verifica tipo, letra, número, fecha y código final. Estas pruebas son
una especificación ejecutable: documentan exactamente qué debe soportar el
proyecto aunque la implementación interna cambie en el futuro.
"""

import pytest

import invoice_parser
from invoices.filename_builder import construir_codigo_comprobante


@pytest.mark.parametrize(
    ("titulo", "tipo", "letra", "codigo"),
    [
        ("FACTURA A", "FACTURA", "A", "FCA"),
        ("FACTURA B", "FACTURA", "B", "FCB"),
        ("FACTURA C", "FACTURA", "C", "FCC"),
        ("NOTA DE CREDITO A", "NOTA DE CREDITO", "A", "NCA"),
        ("NOTA DE CREDITO B", "NOTA DE CREDITO", "B", "NCB"),
        ("NOTA DE CREDITO C", "NOTA DE CREDITO", "C", "NCC"),
        ("NOTA DE DEBITO A", "NOTA DE DEBITO", "A", "NDA"),
        ("NOTA DE DEBITO B", "NOTA DE DEBITO", "B", "NDB"),
        ("NOTA DE DEBITO C", "NOTA DE DEBITO", "C", "NDC"),
    ],
)
def test_nueve_comprobantes_fiscales(titulo, tipo, letra, codigo):
    texto = f"""{titulo}
Nº 0004-00000125
Fecha de Emisión: 01/08/2026
CUIT: 30-12345678-9
"""
    datos = invoice_parser.extraer_datos_factura(texto).datos

    assert datos.tipo_comprobante == tipo
    assert datos.letra_comprobante == letra
    assert datos.numero_comprobante == "00004-00000125"
    assert datos.fecha_emision == "01/08/2026"
    assert construir_codigo_comprobante(tipo, letra, datos.numero_comprobante) == (
        codigo + "00004-00000125"
    )


def test_abreviaturas_nc_y_nd_tambien_se_reconocen():
    assert invoice_parser.detectar_tipo_comprobante("N/C C Nº 1-25") == "NOTA DE CREDITO"
    assert invoice_parser.detectar_tipo_comprobante("N/D B Nº 2-30") == "NOTA DE DEBITO"
