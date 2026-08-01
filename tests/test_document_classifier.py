"""Pruebas del clasificador que separa facturas de listas comerciales."""

from documents import TipoDocumento, clasificar_documento


def test_clasifica_factura_con_formato_desordenado():
    texto = "24/07/2026 A 00020-00047658 FA C T U R A CUIT 30-70844445-2"
    assert clasificar_documento(texto).tipo is TipoDocumento.FACTURA


def test_clasifica_lista_de_precios():
    texto = "CODIGO PRESENTACION PRECIO IVA 21% TOTAL $ X BOTELLA"
    assert clasificar_documento(texto, "LISTA VINOS.pdf").tipo is TipoDocumento.LISTA_PRECIOS
