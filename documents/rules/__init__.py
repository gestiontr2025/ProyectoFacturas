"""Reglas independientes utilizadas por el clasificador documental."""

from documents.rules.administrative import score_administrative_categories
from documents.rules.commercial import score_commercial_categories
from documents.rules.human_resources import score_hr_subcategories

__all__ = [
    "score_administrative_categories",
    "score_commercial_categories",
    "score_hr_subcategories",
]
