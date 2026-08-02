"""Modelo tipado de un comprobante fiscal.

El parser puede encontrar datos parciales: por ejemplo, reconocer que un PDF
es una factura pero no detectar todavía su letra. Por ese motivo los campos
son opcionales y la validación se realiza mediante métodos explícitos, en vez
de impedir la creación del objeto.

Esta decisión es defensiva: conservar información incompleta permite explicar
por qué un documento quedó pendiente sin inventar valores fiscales.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Mapping, Optional


_TIPO_A_PREFIJO = {
    "FACTURA": "FC",
    "NOTA DE CREDITO": "NC",
    "NOTA DE DÉBITO": "ND",
    "NOTA DE DEBITO": "ND",
    "RECIBO": "RC",
}


@dataclass
class FiscalDocument:
    """Representar los datos fiscales extraídos de un único comprobante.

    El modelo no abre PDFs ni ejecuta expresiones regulares. Su función es
    transportar datos de manera uniforme entre parser, validador, organizador
    y presentación. Así evitamos depender de claves de diccionario escritas a
    mano en distintos módulos.
    """

    document_type: Optional[str] = None
    fiscal_letter: Optional[str] = None
    document_number: Optional[str] = None
    issue_date: Optional[str] = None

    issuer_cuit: Optional[str] = None
    issuer_legal_name: Optional[str] = None
    receiver_cuit: Optional[str] = None
    receiver_legal_name: Optional[str] = None

    currency: Optional[str] = None
    subtotal: Optional[str] = None
    taxes: Optional[str] = None
    total_amount: Optional[str] = None
    cae: Optional[str] = None
    cae_expiration: Optional[str] = None

    warnings: list[str] = field(default_factory=list)

    @classmethod
    def from_legacy(cls, datos: Any) -> "FiscalDocument":
        """Adaptar ``DatosFactura`` o un diccionario al modelo nuevo.

        La transición se hace mediante un adaptador en vez de reescribir todo
        el proyecto de una vez. Esto reduce el riesgo de regresiones y permite
        migrar módulo por módulo mientras la API anterior continúa funcionando.
        """
        if isinstance(datos, cls):
            return datos

        if isinstance(datos, Mapping):
            getter = datos.get
        else:
            getter = lambda nombre, default=None: getattr(datos, nombre, default)

        return cls(
            document_type=getter("tipo_comprobante"),
            fiscal_letter=getter("letra_comprobante"),
            document_number=getter("numero_comprobante"),
            issue_date=getter("fecha_emision"),
            issuer_cuit=getter("cuit_emisor"),
            issuer_legal_name=getter("razon_social_emisor"),
            receiver_cuit=getter("cuit_receptor"),
            receiver_legal_name=getter("razon_social_receptor"),
            currency=getter("moneda"),
            subtotal=getter("subtotal"),
            taxes=getter("impuestos"),
            total_amount=getter("importe_total"),
            cae=getter("cae"),
            cae_expiration=getter("vencimiento_cae"),
        )

    @property
    def point_of_sale(self) -> Optional[str]:
        """Devolver el punto de venta contenido en ``document_number``."""
        if not self.document_number or "-" not in self.document_number:
            return None
        return self.document_number.split("-", maxsplit=1)[0]

    @property
    def sequential_number(self) -> Optional[str]:
        """Devolver el número secuencial sin el punto de venta."""
        if not self.document_number or "-" not in self.document_number:
            return None
        return self.document_number.split("-", maxsplit=1)[1]

    @property
    def fiscal_code(self) -> Optional[str]:
        """Construir FCA, NCB, NDC, etc., cuando tipo y letra son válidos."""
        tipo = str(self.document_type or "").strip().upper()
        letra = str(self.fiscal_letter or "").strip().upper()
        prefijo = _TIPO_A_PREFIJO.get(tipo)
        if not prefijo or letra not in {"A", "B", "C"}:
            return None
        return f"{prefijo}{letra}"

    def missing_required_fields(self, *, require_supplier: bool = False, supplier_present: bool = False) -> list[str]:
        """Enumerar campos obligatorios ausentes para organizar el archivo."""
        faltantes: list[str] = []
        if not self.issue_date:
            faltantes.append("fecha de emisión")
        if not self.document_type:
            faltantes.append("tipo de comprobante")
        if not self.fiscal_letter:
            faltantes.append("letra del comprobante")
        if not self.document_number:
            faltantes.append("número de comprobante")
        if require_supplier and not supplier_present:
            faltantes.append("proveedor")
        return faltantes

    def validate_values(self) -> list[str]:
        """Detectar valores presentes pero inválidos sin lanzar excepciones."""
        errores: list[str] = []
        if self.fiscal_letter and self.fiscal_letter.upper() not in {"A", "B", "C"}:
            errores.append(f"Letra fiscal no admitida: {self.fiscal_letter!r}")
        if self.issue_date:
            formatos = ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d")
            if not any(_fecha_valida(self.issue_date, formato) for formato in formatos):
                errores.append(f"Fecha de emisión inválida: {self.issue_date!r}")
        return errores

    def to_dict(self) -> dict[str, Any]:
        """Convertir el modelo a datos simples para JSON, logs o depuración."""
        return asdict(self)


def _fecha_valida(valor: str, formato: str) -> bool:
    try:
        datetime.strptime(valor, formato)
    except (TypeError, ValueError):
        return False
    return True
