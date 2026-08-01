"""Pruebas de regresión para formatos reales de facturas del proyecto.

Estas pruebas documentan errores que ya ocurrieron. Su objetivo es impedir que
una refactorización futura vuelva a romper formatos que sabemos interpretar.
"""

import invoice_parser


def test_factura_horeca_con_numero_separado_por_espacios():
    texto = """Fecha: 31/07/2026
FACTURA
A
Nº 0006 - 00343487
C.U.I.T.: 30-71209619-1
MADERO ROOF TOP S. A.
"""
    datos = invoice_parser.extraer_datos_factura(texto).datos
    assert datos.tipo_comprobante == "FACTURA"
    assert datos.letra_comprobante == "A"
    assert datos.numero_comprobante == "00006-00343487"
    assert datos.fecha_emision == "31/07/2026"


def test_factura_prados_con_titulo_espaciado():
    texto = """24/07/2026
A 00020-00047658
FA C T U R A
Nº:
MADERO ROOF TOP S. A.
"""
    datos = invoice_parser.extraer_datos_factura(texto).datos
    assert datos.tipo_comprobante == "FACTURA"
    assert datos.letra_comprobante == "A"
    assert datos.numero_comprobante == "00020-00047658"
    assert datos.fecha_emision == "24/07/2026"


def test_lista_de_precios_no_se_interpreta_como_factura():
    texto = """CODIGO PRODUCTO PRESENTACION PRECIO IVA 21% TOTAL
00100100202 ZUCCARDI 2023 6 X 750 CC $ 135.000,00
"""
    datos = invoice_parser.extraer_datos_factura(texto).datos
    assert datos.tipo_comprobante is None
    assert datos.letra_comprobante is None
    assert datos.numero_comprobante is None
    assert datos.fecha_emision is None


def test_detecta_letra_antes_de_factura_espaciada():
    texto = """
    24/07/2026
    A 00020-00047658
    GUILLERMO GARCIA
    FA C T U R A
    Nº:
    """
    assert invoice_parser.detectar_letra_comprobante(texto) == "A"
    assert invoice_parser.detectar_numero_comprobante(texto) == "00020-00047658"
