"""Regresiones basadas en disposiciones reales observadas en proveedores.

Los fragmentos representan el texto que un extractor de PDF puede entregar.
No almacenamos facturas reales dentro del repositorio porque contienen datos
comerciales; conservamos únicamente las líneas mínimas necesarias para probar
la estructura fiscal.
"""

import invoice_parser


def test_formato_arca_factura_c_con_letra_antes_del_tipo():
    texto = """
Fecha de Emisión:
21/07/2026
Punto de Venta: 00002 Comp. Nro: 00000308
C FACTURA
COD. 011
"""
    datos = invoice_parser.extraer_datos_factura(texto).datos

    assert datos.tipo_comprobante == "FACTURA"
    assert datos.letra_comprobante == "C"
    assert datos.numero_comprobante == "00002-00000308"
    assert datos.fecha_emision == "21/07/2026"


def test_formato_arca_chesko_factura_c():
    texto = """
Fecha de Emisión:
31/07/2026
Punto de Venta: 00001 Comp. Nro: 00000393
C FACTURA
COD. 011
"""
    datos = invoice_parser.extraer_datos_factura(texto).datos

    assert datos.letra_comprobante == "C"
    assert datos.numero_comprobante == "00001-00000393"


def test_formato_colppy_factura_a_con_codigo_antes_del_tipo():
    texto = """
A
COD 01
Factura
Punto de Venta: 0004 Comp. Nro: 00219487
Fecha de Emisión: 24/07/2026
"""
    datos = invoice_parser.extraer_datos_factura(texto).datos

    assert datos.tipo_comprobante == "FACTURA"
    assert datos.letra_comprobante == "A"
    assert datos.numero_comprobante == "00004-00219487"
    assert datos.fecha_emision == "24/07/2026"


def test_disposicion_lineal_real_de_pypdf_en_comprobante_arca():
    texto = """
FECHA DE EMISION: ORIGINAL
PERIODO FACTURADO DESDE: HASTA: FECHA DE VTO. PARA EL PAGO:
21/07/2026 21/07/2026 29/07/2026 21/07/2026
PUNTO DE VENTA: COMP. NRO:00002 00000308
FACTURACCOD. 011
"""
    datos = invoice_parser.extraer_datos_factura(texto).datos

    assert datos.tipo_comprobante == "FACTURA"
    assert datos.letra_comprobante == "C"
    assert datos.numero_comprobante == "00002-00000308"
    assert datos.fecha_emision == "21/07/2026"
