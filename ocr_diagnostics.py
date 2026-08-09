"""Utilidades de diagnóstico OCR para v0.36.

Este módulo centraliza metadatos de candidatos OCR y rotaciones.
La integración funcional se realiza desde pdf_reader.py.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Iterable


@dataclass(frozen=True)
class OCRCandidate:
    metodo: str
    puntaje: int
    texto: str
    rotacion: int = 0

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def serialize_candidates(candidates: Iterable[OCRCandidate]) -> list[dict[str, object]]:
    return [candidate.as_dict() for candidate in candidates]
