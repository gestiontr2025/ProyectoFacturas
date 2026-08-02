"""Reglas para documentos comerciales no fiscales."""

from __future__ import annotations

from documents.rules.common import contains_any, matches_any


def score_commercial_categories(content: str, filename: str) -> dict[str, int]:
    """Puntuar listas de precios, menús/cartas y estados de cuenta."""

    joined = f"{filename} {content}"

    price_list = 0
    price_list += 8 * contains_any(filename, ("LISTA DE PRECIOS", "LISTAS DE PRECIOS"))
    price_list += 9 * contains_any(content, ("LISTA DE PRECIOS", "LISTA DE PRECIOS ACTUALIZADA"))
    # Algunos PDF de catálogos extraen cada carácter con espacios. El patrón
    # conserva las palabras completas y no se activa por una mención aislada
    # de ``precio`` dentro de una factura.
    price_list += 10 * matches_any(content, (r"L\s*I\s*S\s*T\s*A\s+D\s*E\s+P\s*R\s*E\s*C\s*I\s*O\s*S",))
    price_list += 5 * matches_any(filename, (r"^LISTA\b", r"\bLISTA\s+ACEITES\b"))
    price_list += 2 * contains_any(content, ("CODIGO", "PRESENTACION", "PRECIO", "PRECIO SUGERIDO", "$ X BOTELLA", "$ X UNID"))

    menu = 0
    menu += 8 * contains_any(filename, ("MENU", "CARTA", "VINOSCARTAFINAL"))
    menu += 5 * contains_any(content, ("MENU", "CARTA DE VINOS", "PLATOS", "COCTELES"))
    if "PRECIO" in content and contains_any(joined, ("MENU", "CARTA")):
        menu += 2

    account_statement = 0
    account_statement += 8 * contains_any(filename, ("CTA CTE", "CTA_CTE", "CUENTA CORRIENTE", "ESTADO DE CUENTA"))
    account_statement += 7 * contains_any(content, ("ESTADO DE CUENTA", "CUENTA CORRIENTE"))
    account_statement += 2 * contains_any(content, ("SALDO ANTERIOR", "DEBE", "HABER", "SALDO"))
    account_statement += 8 * contains_any(content, ("COMPOSICION DE SALDOS",))

    remito_receipt = 0
    remito_receipt += 7 * matches_any(filename, (r"^INV-\d+", r"^REMITO[_ -]", r"^RECIBO[_ -]"))
    remito_receipt += 8 * contains_any(content, ('RECIBO "X"', "RECIBO X", "REMITO"))
    remito_receipt += 10 * contains_any(content, ("DOCUMENTO NO VALIDO COMO FACTURA", "RECIBO OFICIAL"))
    # La combinación INV + recibo X identifica el comprobante comercial
    # observado sin convertirlo en una factura fiscal A/B/C.
    if "INV-" in joined and contains_any(content, ('RECIBO "X"', "RECIBO X")):
        remito_receipt += 5

    return {
        "lista_de_precios": price_list,
        "menus_y_cartas": menu,
        "estados_de_cuenta": account_statement,
        "remitos_y_recibos": remito_receipt,
    }
