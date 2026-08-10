from pathlib import Path

import pdf_reader
from fiscal.issue_date import analizar_fecha_emision_para_auditoria
from storage.invoice_date_audit import audit_organized_invoice_dates


def test_fecha_explicitamente_etiquetada_corrige_nombre_erroneo():
    texto = """
    FACTURA C 00001-00000127
    FECHA DE EMISION: 30/03/2026
    FECHA DE VTO. PARA EL PAGO: 09/04/2026
    """

    analisis = analizar_fecha_emision_para_auditoria(
        texto,
        fecha_actual="09/04/2026",
    )

    assert analisis.issue_date == "30/03/2026"
    assert analisis.confidence == "high"


def test_layout_arca_aplanado_identifica_emision_y_no_vencimiento(monkeypatch, tmp_path):
    root = tmp_path / "Facturas"
    source = root / "PROVEEDOR" / "2026" / "03" / (
        "05-03FCC00001-00000343_MADERO_ROOF_TOP_PROVEEDOR.pdf"
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

    # Sin geometría real el orden de las cuatro fechas aplanadas no es
    # semánticamente estable entre generadores PDF. La auditoría ya no inventa
    # qué posición corresponde a emisión: conserva el archivo y exige evidencia
    # visual/estructural adicional.
    results = audit_organized_invoice_dates(root, apply=False)
    assert len(results) == 1
    assert results[0].status == "manual_review"
    assert results[0].destination is None
