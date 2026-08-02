"""Regresiones funcionales para familias descubiertas en _Pendientes."""

from documents import TipoDocumento, clasificar_documento
from fiscal.issue_date import detectar_fecha_emision
from suppliers.filename_evidence import detectar_identificador_por_nombre
import supplier_catalog


def test_fecha_sin_etiqueta_es_aceptable_solo_con_contexto_fiscal():
    texto = """
    A00031-00073820
    ORIGINAL
    27/06/2025
    MADERO ROOF TOP S. A.
    """
    assert detectar_fecha_emision(texto) is None
    assert detectar_fecha_emision(texto, contexto_fiscal_confirmado=True) == "27/06/2025"


def test_nota_credito_los_prados_por_nombre():
    nombre = "CA_002000004666_20260304_011454_20260305_05_34_35.pdf"
    assert detectar_identificador_por_nombre(nombre) == "frigorifico_los_prados"


def test_familia_gifel_por_nombre_altamente_especifico():
    assert detectar_identificador_por_nombre("FACA0003100073820.pdf") == "gifel_s_r_l"
    assert supplier_catalog.obtener_proveedor_por_identificador("gifel_s_r_l") is not None


def test_familia_nuevo_emporio_por_nombre_altamente_especifico():
    assert detectar_identificador_por_nombre("FACB0000700216606.pdf") == "el_nuevo_emporio_sa"


def test_invoice_recibo_x_no_se_clasifica_como_factura_fiscal():
    texto = '''
    Recibo "X"
    N.º de factura INV-016860
    Fecha de la factura : 10 feb 2026
    Total ARS143,650.00
    '''
    resultado = clasificar_documento(texto, "INV-016860.pdf")
    assert resultado.tipo is TipoDocumento.REMITO_RECIBO


def test_comunicacion_envairo_se_archiva_como_comunicacion():
    texto = """
    COMUNICACIÓN A CLIENTES
    PROGRAMA DE INTEGRIDAD ENVAIRO
    Código de Ética y Conducta Empresarial
    Política Anticorrupción
    """
    resultado = clasificar_documento(texto, "Nota a Clientes ENVAIRO.pdf")
    assert resultado.tipo is TipoDocumento.COMUNICACION


def test_alta_arca_plural_se_clasifica_como_rrhh():
    resultado = clasificar_documento(
        "CONSTANCIA DE ALTA DE RELACIONES LABORALES ARCA",
        "2025-11 Madero Alta arca 4 empleados.pdf",
    )
    assert resultado.tipo is TipoDocumento.RRHH_ALTAS_BAJAS
