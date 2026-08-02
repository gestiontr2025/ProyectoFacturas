"""Pruebas del clasificador que separa facturas de listas comerciales."""

from documents import TipoDocumento, clasificar_documento


def test_clasifica_factura_con_formato_desordenado():
    texto = "24/07/2026 A 00020-00047658 FA C T U R A CUIT 30-70844445-2"
    assert clasificar_documento(texto).tipo is TipoDocumento.FACTURA


def test_clasifica_lista_de_precios():
    texto = "CODIGO PRESENTACION PRECIO IVA 21% TOTAL $ X BOTELLA"
    assert clasificar_documento(texto, "LISTA VINOS.pdf").tipo is TipoDocumento.LISTA_PRECIOS


def test_clasifica_comprobante_de_pago_por_nombre():
    resultado = clasificar_documento(
        "Transferencia realizada. Importe pagado.",
        "23-07ComprobanteDePago_EMPRESA_PROVEEDOR.pdf",
    )
    assert resultado.tipo is TipoDocumento.COMPROBANTE_PAGO


def test_clasifica_orden_de_pago_por_nombre():
    resultado = clasificar_documento(
        "Beneficiario y comprobantes imputados.",
        "23-07OP0001-00002227_EMPRESA_PROVEEDOR.pdf",
    )
    assert resultado.tipo is TipoDocumento.ORDEN_PAGO
