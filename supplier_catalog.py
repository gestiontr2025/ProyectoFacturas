"""Catálogo canónico de proveedores cargado desde JSON.

El archivo ``suppliers/data/supplier_catalog.json`` es la única fuente de
verdad utilizada durante la ejecución normal. El código de este módulo se
limita a validar, indexar y consultar esos datos.

Separar datos y lógica tiene una ventaja importante: agregar o actualizar
proveedores ya no exige modificar Python. El catálogo se regenera desde el
Excel de comprobantes recibidos mediante ``tools/import_afip_suppliers.py``.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import json
from pathlib import Path
import re
from typing import Iterable, Optional
import unicodedata

import business_config

CATALOG_PATH = Path(__file__).resolve().parent / "suppliers" / "data" / "supplier_catalog.json"


@dataclass(frozen=True)
class Proveedor:
    """Identidad fiscal y comercial inmutable de un proveedor."""

    identificador: str
    razon_social: str
    nombre_fantasia: Optional[str]
    cuit: str
    nombre_carpeta: Optional[str] = None
    tipos_comprobante_observados: tuple[str, ...] = ()
    alicuotas_iva_observadas: tuple[float, ...] = ()
    otros_tributos_observados: bool = False
    monedas_observadas: tuple[str, ...] = ()
    cantidad_comprobantes_observados: int = 0
    alias_busqueda: tuple[str, ...] = ()

    def cuit_sin_guiones(self) -> str:
        return "".join(caracter for caracter in self.cuit if caracter.isdigit())

    def nombre_preferido(self) -> str:
        return self.nombre_fantasia or self.razon_social

    def convertir_a_diccionario(self) -> dict:
        return {
            "identificador": self.identificador,
            "razon_social": self.razon_social,
            "nombre_fantasia": self.nombre_fantasia,
            "nombre_carpeta": self.nombre_carpeta,
            "cuit": self.cuit,
            "cuit_sin_guiones": self.cuit_sin_guiones(),
            "tipos_comprobante_observados": self.tipos_comprobante_observados,
            "alicuotas_iva_observadas": self.alicuotas_iva_observadas,
            "otros_tributos_observados": self.otros_tributos_observados,
            "monedas_observadas": self.monedas_observadas,
            "cantidad_comprobantes_observados": self.cantidad_comprobantes_observados,
            "alias_busqueda": self.alias_busqueda,
        }


def normalizar_texto_busqueda(valor: object) -> str:
    """Crear una representación comparable sin alterar el dato canónico."""
    if valor is None:
        return ""
    texto = unicodedata.normalize("NFKC", str(valor))
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    texto = texto.upper()
    texto = re.sub(r"[^A-Z0-9]+", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


def normalizar_cuit(cuit: object) -> Optional[str]:
    """Normalizar un CUIT al formato XX-XXXXXXXX-X."""
    if cuit is None:
        return None
    digitos = "".join(c for c in str(cuit) if c.isdigit())
    if len(digitos) != 11:
        return None
    return f"{digitos[:2]}-{digitos[2:10]}-{digitos[10]}"


def generar_alias_automaticos(razon_social: str, nombre_fantasia: Optional[str]) -> tuple[str, ...]:
    """Generar alias seguros a partir de nombres canónicos."""
    candidatos = {razon_social}
    if nombre_fantasia:
        candidatos.add(nombre_fantasia)
    return tuple(sorted({normalizar_texto_busqueda(v) for v in candidatos if v}))


def _leer_json_catalogo(path: Path = CATALOG_PATH) -> dict:
    if not path.exists():
        raise RuntimeError(f"No se encontró el catálogo de proveedores: {path}")
    try:
        contenido = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"No fue posible leer el catálogo de proveedores: {path}") from exc
    if not isinstance(contenido, dict) or not isinstance(contenido.get("suppliers"), list):
        raise RuntimeError("El catálogo JSON no cumple el esquema esperado.")
    return contenido


def _crear_proveedor(registro: dict) -> Proveedor:
    observado = registro.get("observed") or {}
    aliases = set(generar_alias_automaticos(registro["legal_name"], registro.get("display_name")))
    aliases.update(normalizar_texto_busqueda(a) for a in registro.get("aliases", []) if a)
    return Proveedor(
        identificador=str(registro["identifier"]).strip(),
        razon_social=str(registro["legal_name"]).strip(),
        nombre_fantasia=(str(registro["display_name"]).strip() if registro.get("display_name") else None),
        cuit=normalizar_cuit(registro.get("cuit")) or "",
        nombre_carpeta=(str(registro["folder_name"]).strip() if registro.get("folder_name") else None),
        tipos_comprobante_observados=tuple(str(v) for v in observado.get("document_types", [])),
        alicuotas_iva_observadas=tuple(float(v) for v in observado.get("vat_rates", [])),
        otros_tributos_observados=bool(observado.get("other_taxes", False)),
        monedas_observadas=tuple(str(v) for v in observado.get("currencies", [])),
        cantidad_comprobantes_observados=int(observado.get("document_count", 0)),
        alias_busqueda=tuple(sorted(a for a in aliases if a)),
    )


def validar_catalogo(proveedores: Iterable[Proveedor] | None = None) -> None:
    """Fallar temprano ante datos duplicados o incompletos."""
    elementos = tuple(proveedores if proveedores is not None else PROVEEDORES.values())
    ids: set[str] = set()
    cuits: set[str] = set()
    for proveedor in elementos:
        if not proveedor.identificador or proveedor.identificador in ids:
            raise RuntimeError(f"Identificador de proveedor inválido o repetido: {proveedor.identificador!r}")
        ids.add(proveedor.identificador)
        if not proveedor.razon_social:
            raise RuntimeError(f"Proveedor sin razón social: {proveedor.identificador}")
        cuit = proveedor.cuit_sin_guiones()
        if len(cuit) != 11 or cuit in cuits:
            raise RuntimeError(f"CUIT inválido o repetido: {proveedor.cuit!r}")
        cuits.add(cuit)
        if business_config.es_cuit_receptor(proveedor.cuit):
            raise RuntimeError("La empresa receptora no puede figurar como proveedor.")
        if proveedor.cantidad_comprobantes_observados < 2:
            raise RuntimeError(
                f"{proveedor.identificador} no cumple el mínimo de dos comprobantes observados."
            )


_CATALOGO_RAW = _leer_json_catalogo()
PROVEEDORES: dict[str, Proveedor] = {
    proveedor.identificador: proveedor
    for proveedor in (_crear_proveedor(item) for item in _CATALOGO_RAW["suppliers"])
}
validar_catalogo(PROVEEDORES.values())
_PROVEEDORES_POR_CUIT = {p.cuit_sin_guiones(): p for p in PROVEEDORES.values()}


def obtener_proveedor(identificador: str) -> Optional[Proveedor]:
    if not isinstance(identificador, str):
        return None
    return PROVEEDORES.get(identificador.strip())


def obtener_proveedor_por_identificador(identificador: str) -> Optional[Proveedor]:
    """Alias explícito conservado para compatibilidad con módulos existentes."""
    return obtener_proveedor(identificador)


def obtener_proveedor_obligatorio(identificador: str) -> Proveedor:
    proveedor = obtener_proveedor(identificador)
    if proveedor is None:
        raise KeyError(f"Proveedor desconocido: {identificador}")
    return proveedor


def buscar_proveedor_por_cuit(cuit: object) -> Optional[Proveedor]:
    normalizado = normalizar_cuit(cuit)
    if normalizado is None:
        return None
    return _PROVEEDORES_POR_CUIT.get("".join(c for c in normalizado if c.isdigit()))


def buscar_proveedores_en_texto(texto: object) -> tuple[Proveedor, ...]:
    """Devolver proveedores cuya razón social, alias o CUIT aparece en el texto."""
    texto_original = "" if texto is None else str(texto)
    normalizado = normalizar_texto_busqueda(texto_original)
    digitos = "".join(c for c in texto_original if c.isdigit())
    encontrados: list[Proveedor] = []
    for proveedor in PROVEEDORES.values():
        if proveedor.cuit_sin_guiones() in digitos:
            encontrados.append(proveedor)
            continue
        if any(alias and alias in normalizado for alias in proveedor.alias_busqueda):
            encontrados.append(proveedor)
    return tuple(encontrados)


def listar_proveedores() -> tuple[Proveedor, ...]:
    return tuple(sorted(PROVEEDORES.values(), key=lambda p: p.identificador))


def cantidad_proveedores() -> int:
    return len(PROVEEDORES)
