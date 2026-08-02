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


def test_clasifica_alta_baja_de_recursos_humanos():
    resultado = clasificar_documento(
        "Constancia emitida por ARCA para la baja de una relación laboral.",
        "2026-02 Madero baja arca Gomez Figueredo.pdf",
    )
    assert resultado.tipo is TipoDocumento.RRHH_ALTAS_BAJAS


def test_clasifica_liquidacion_final():
    resultado = clasificar_documento(
        "Liquidación final. Remuneración, vacaciones e indemnización.",
        "Liquidación_MAYO 2026 LIQ FINAL_Empleado.pdf",
    )
    assert resultado.tipo is TipoDocumento.RRHH_LIQUIDACIONES


def test_clasifica_recibo_de_haberes_por_legajo():
    resultado = clasificar_documento(
        "RECIBO DE HABERES. Aportes y contribuciones.",
        "DICIEMBRE2025_Legajo_23_Empleado.pdf",
    )
    assert resultado.tipo is TipoDocumento.RRHH_RECIBOS_LEGAJOS


def test_clasifica_lista_por_nombre_evidente():
    resultado = clasificar_documento(
        "Aceite de oliva presentación precio por unidad.",
        "Lista Aceites 13 Feb 2026_BASE.pdf",
    )
    assert resultado.tipo is TipoDocumento.LISTA_PRECIOS


def test_clasifica_menu_o_carta():
    resultado = clasificar_documento(
        "Carta de vinos con etiquetas y precios.",
        "VinosCartaFinal.pdf",
    )
    assert resultado.tipo is TipoDocumento.MENUS_CARTAS


def test_clasifica_instructivo():
    resultado = clasificar_documento(
        "Instrucciones paso a paso para operar la plataforma.",
        "INSTRUCTIVO PAGO ONLINE CUENTA CTE.pdf",
    )
    assert resultado.tipo is TipoDocumento.INSTRUCTIVO


def test_documento_ambiguo_permanece_desconocido():
    resultado = clasificar_documento("Documento general", "comprobante.pdf")
    assert resultado.tipo is TipoDocumento.DESCONOCIDO
