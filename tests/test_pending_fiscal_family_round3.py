from pathlib import Path
import json

from documents import TipoDocumento, clasificar_documento
from suppliers.ad_hoc import detectar_emisor_no_recurrente
from suppliers.filename_evidence import detectar_identificador_por_nombre


def test_el_nuevo_emporio_filename_families():
    assert detectar_identificador_por_nombre('FACA0000700057929.pdf') == 'el_nuevo_emporio_sa'
    assert detectar_identificador_por_nombre('FACA0001000015273.pdf') == 'el_nuevo_emporio_sa'
    assert detectar_identificador_por_nombre('N CB0001000000768.pdf') == 'el_nuevo_emporio_sa'


def test_souverain_filename_family():
    assert detectar_identificador_por_nombre('20260618140336_Comprobante-FCVTA-A-2-85876.pdf') == 'buenos_ayres_vinos_y_bebidas_s_a'


def test_one_time_supplier_does_not_require_catalog_entry():
    result = detectar_emisor_no_recurrente('Razón Social: AUREA VINOS SRL CUIT 30-71538851-7')
    assert result and result['proveedor_detectado'] is True
    assert result['cuit_canonico'] == '30-71538851-7'
    assert result['metodo_deteccion'] == 'encabezado_fiscal_no_persistente'


def test_non_fiscal_pending_families_are_classified():
    assert clasificar_documento('INMOBILIARIO Y ABL', '3702130.pdf').tipo is TipoDocumento.IMPUESTOS_SERVICIOS
    assert clasificar_documento('', 'CCF_000455.pdf').tipo is TipoDocumento.CONSORCIO
    assert clasificar_documento('PLAZA 1 PREPARACIONES PRODUCIR', 'MEP PLAZAS T&R.pdf').tipo is TipoDocumento.OPERATIVO
    assert clasificar_documento('Documento No Válido como Factura X RECIBO', 'RDRC596270.pdf').tipo is TipoDocumento.REMITO_RECIBO
    assert clasificar_documento('Ingreso a Factura Ya contraseña provisoria', 'Acceso - Factura Ya.pdf').tipo is TipoDocumento.INSTRUCTIVO
