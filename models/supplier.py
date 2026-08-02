"""Modelo tipado de un proveedor reconocido por el proyecto."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Optional


@dataclass
class Supplier:
    """Representar la identidad comercial y fiscal de un proveedor.

    ``legal_name`` se utiliza para identificar legalmente al emisor y formar
    el nombre del PDF. ``display_name`` puede ser un nombre comercial más
    cómodo para navegar carpetas, como ``Colppy``.
    """

    detected: bool = False
    identifier: Optional[str] = None
    legal_name: Optional[str] = None
    display_name: Optional[str] = None
    cuit: Optional[str] = None
    detection_method: str = "sin_coincidencias"
    confidence: str = "ninguna"
    score: int = 0
    warnings: list[str] = field(default_factory=list)

    @classmethod
    def from_detection_result(cls, resultado: Mapping[str, Any] | None) -> "Supplier":
        """Adaptar la respuesta histórica de ``supplier_detector``.

        El detector continuará devolviendo diccionarios durante la transición.
        El resto del código puede trabajar desde ahora con atributos tipados.
        """
        resultado = resultado or {}
        legal_name = resultado.get("razon_social_canonica") or resultado.get("razon_social_encontrada")
        display_name = resultado.get("nombre_fantasia") or resultado.get("nombre_proveedor") or legal_name
        return cls(
            detected=bool(resultado.get("proveedor_detectado")),
            identifier=resultado.get("identificador"),
            legal_name=legal_name,
            display_name=display_name,
            cuit=resultado.get("cuit_canonico") or resultado.get("cuit_encontrado"),
            detection_method=str(resultado.get("metodo_deteccion") or "sin_coincidencias"),
            confidence=str(resultado.get("nivel_confianza") or "ninguna"),
            score=int(resultado.get("puntaje") or 0),
            warnings=list(resultado.get("advertencias") or []),
        )

    @property
    def folder_name(self) -> str:
        """Elegir el nombre legible usado para la carpeta del proveedor."""
        return str(self.display_name or self.legal_name or "PROVEEDOR_DESCONOCIDO").strip()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
