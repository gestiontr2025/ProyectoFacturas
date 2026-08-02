"""Normalización mínima compartida por los detectores fiscales.

La normalización elimina diferencias visuales que no cambian el significado:
tildes, mayúsculas, espacios repetidos y determinados símbolos. No modifica
números ni inventa información ausente.
"""

import re
import unicodedata


def normalizar_para_busqueda(texto: str) -> str:
    """Preparar texto para búsquedas tolerantes mediante expresiones regulares."""
    if not isinstance(texto, str):
        return ""
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = texto.upper().replace("º", "O").replace("°", "O")
    return re.sub(r"\s+", " ", texto).strip()
