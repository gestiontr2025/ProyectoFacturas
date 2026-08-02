"""Utilidades compartidas por las reglas de clasificación documental.

Las reglas reciben texto ya normalizado y devuelven un puntaje entero. Un
puntaje alto significa que existen varias señales independientes de la misma
categoría. Esta estrategia evita depender de una sola palabra ambigua.
"""

from __future__ import annotations

import re


def contains_any(text: str, terms: tuple[str, ...]) -> int:
    """Contar cuántos términos distintos aparecen en ``text``."""

    return sum(1 for term in terms if term in text)


def matches_any(text: str, patterns: tuple[str, ...]) -> int:
    """Contar cuántas expresiones regulares diferentes coinciden."""

    return sum(1 for pattern in patterns if re.search(pattern, text))
