from pathlib import Path

import pdf_reader
from fiscal.issue_date import detectar_fecha_emision_para_auditoria
from storage.invoice_date_audit import audit_organized_invoice_dates


def test_auditoria_conserva_fecha_actual_si_aparece_fuera_de_contexto_excluido():
    texto = """
    FECHA DE EMISION: ORIGINAL
    PERIODO FACTURADO DESDE: HASTA: FECHA DE VTO. PARA EL PAGO:
    02/03/2026 02/03/2026 02/03/2026 12/03/2026
    PUNTO DE VENTA: 00001 COMP. NRO: 00000343
    C FACTURA COD. 011
    """

    assert detectar_fecha_emision_para_auditoria(
        texto,
        fecha_actual="02/03/2026",
    ) == "02/03/2026"


def test_auditoria_no_usa_vencimiento_diez_dias_despues_como_emision(monkeypatch, tmp_path):
    root = tmp_path / "Facturas"
    source = root / "CHESKO_AGUSTIN_EZEQUIEL" / "2026" / "03" / (
        "02-03FCC00001-00000343_MADERO_ROOF_TOP_CHESKO_AGUSTIN_EZEQUIEL.pdf"
    )
    source.parent.mkdir(parents=True)
    source.write_bytes(b"%PDF placeholder")

    texto = """
    FECHA DE EMISION: ORIGINAL
    PERIODO FACTURADO DESDE: HASTA: FECHA DE VTO. PARA EL PAGO:
    02/03/2026 02/03/2026 02/03/2026 12/03/2026
    PUNTO DE VENTA: 00001 COMP. NRO: 00000343
    C FACTURA COD. 011
    """

    monkeypatch.setattr(
        pdf_reader,
        "leer_pdf",
        lambda *_args, **_kwargs: {"texto_completo": texto},
    )

    assert audit_organized_invoice_dates(root, apply=False) == []


def test_auditoria_dba_corrige_inicio_actividad_sin_confundirlo_con_emision(monkeypatch, tmp_path):
    root = tmp_path / "Facturas"
    source = root / "DBA" / "2006" / "04" / (
        "01-04FCA00013-00189814_MADERO_ROOF_TOP_DISTRIBUIDORA_DE_BEBIDAS_SRL.pdf"
    )
    source.parent.mkdir(parents=True)
    source.write_bytes(b"%PDF placeholder")

    texto = """
    A
    06/08/2026 Fecha:
    Nro: 00013-00189814
    Distribuidora de Bebidas SRL
    CUIT: 30-70942442-0
    INICIO ACTIV.:
    01/04/2006
    FACTURA
    CAE: 86327172503529
    16/08/2026 Fecha Vencimiento CAE:
    """

    monkeypatch.setattr(
        pdf_reader,
        "leer_pdf",
        lambda *_args, **_kwargs: {"texto_completo": texto},
    )

    results = audit_organized_invoice_dates(root, apply=False)

    assert len(results) == 1
    assert results[0].status == "would_move"
    assert results[0].destination == root / "DBA" / "2026" / "08" / (
        "06-08FCA00013-00189814_MADERO_ROOF_TOP_DISTRIBUIDORA_DE_BEBIDAS_SRL.pdf"
    )


def test_auditoria_bloquea_fecha_futura(monkeypatch, tmp_path):
    root = tmp_path / "Facturas"
    source = root / "COLMAN_TOMAS_AGUSTIN" / "2026" / "08" / (
        "05-08FCC00001-00000046_MADERO_ROOF_TOP_COLMAN_TOMAS_AGUSTIN.pdf"
    )
    source.parent.mkdir(parents=True)
    source.write_bytes(b"%PDF placeholder")

    monkeypatch.setattr(
        pdf_reader,
        "leer_pdf",
        lambda *_args, **_kwargs: {
            "texto_completo": "Fecha de Emision: 15/08/2099 C FACTURA 00001-00000046"
        },
    )

    results = audit_organized_invoice_dates(root, apply=False)

    assert len(results) == 1
    assert results[0].status == "blocked_future_date"
    assert results[0].destination is None
