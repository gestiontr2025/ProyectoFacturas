"""Normalización de textos destinados a nombres de archivos y carpetas."""

import re
import unicodedata


def normalizar_componente_ruta(valor: str, valor_por_defecto: str = "DESCONOCIDO") -> str:
    """Convertir un nombre humano en un componente seguro para Windows.

    Se eliminan tildes, signos y espacios porque los nombres finales deben ser
    estables aunque el proveedor escriba su razón social de distintas formas.
    Por ejemplo, ``Hóreca S.R.L.`` se convierte en ``HORECA_SRL``.
    """
    if not valor or not str(valor).strip():
        return valor_por_defecto

    texto = unicodedata.normalize("NFKD", str(valor))
    texto = "".join(caracter for caracter in texto if not unicodedata.combining(caracter))
    texto = texto.upper()
    texto = re.sub(r"[^A-Z0-9]+", "_", texto)
    texto = re.sub(r"_+", "_", texto).strip("_")
    return texto or valor_por_defecto


def quitar_tipo_societario(nombre: str) -> str:
    """Quitar un sufijo societario cuando forma parte del nombre receptor.

    El formato acordado usa ``MADERO_ROOF_TOP`` y no
    ``MADERO_ROOF_TOP_SA``. Esta función solo elimina sufijos al final para no
    alterar palabras legítimas ubicadas en el medio del nombre.
    """
    normalizado = normalizar_componente_ruta(nombre)
    return re.sub(r"_(S_A|SA|S_R_L|SRL)$", "", normalizado).rstrip("_")
