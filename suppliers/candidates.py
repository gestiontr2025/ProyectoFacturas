"""Registro local de proveedores ocasionales observados por el programa.

El catálogo JSON contiene únicamente proveedores recurrentes y confirmados.
Este módulo guarda, por separado, emisores detectados directamente desde una
factura válida para poder contar sus apariciones sin convertirlos de manera
automática en proveedores habituales.

El archivo se crea dentro de ``data/`` y no forma parte de la fuente de verdad
del catálogo. Puede borrarse sin afectar el procesamiento de facturas.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import config


def _load(path: Path) -> dict[str, Any]:
    """Leer el registro existente o devolver una estructura vacía segura."""
    if not path.exists():
        return {"schema_version": 1, "candidates": {}}

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        # Un registro auxiliar dañado nunca debe impedir organizar una factura.
        return {"schema_version": 1, "candidates": {}}

    if not isinstance(data, dict) or not isinstance(data.get("candidates"), dict):
        return {"schema_version": 1, "candidates": {}}
    return data


def _atomic_write(path: Path, data: dict[str, Any]) -> None:
    """Guardar mediante reemplazo atómico para evitar archivos parciales."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def registrar_proveedor_ocasional(
    *,
    cuit: str,
    business_name: str,
    document_key: str,
    folder_name: str,
    path: Path | None = None,
) -> dict[str, Any]:
    """Registrar una aparición única sin promover el proveedor al catálogo.

    ``document_key`` evita incrementar el contador cuando el mismo comprobante
    se reprocesa más de una vez. La promoción a proveedor habitual queda como
    una decisión humana: el programa solo conserva evidencia y frecuencia.
    """
    destination = Path(path or config.SUPPLIER_CANDIDATES_PATH)
    data = _load(destination)
    candidates = data["candidates"]

    normalized_cuit = "".join(character for character in cuit if character.isdigit())
    if len(normalized_cuit) != 11:
        return {"registered": False, "reason": "invalid_cuit"}

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    record = candidates.setdefault(
        normalized_cuit,
        {
            "cuit": cuit,
            "business_name": business_name,
            "folder_name": folder_name,
            "occurrences": 0,
            "first_seen": now,
            "last_seen": now,
            "document_keys": [],
            "status": "candidate",
        },
    )

    keys = record.setdefault("document_keys", [])
    if document_key in keys:
        return {"registered": False, "reason": "already_registered", "record": record}

    keys.append(document_key)
    record["occurrences"] = len(keys)
    record["last_seen"] = now
    record["business_name"] = business_name
    record["folder_name"] = folder_name
    record["suggest_catalog_review"] = record["occurrences"] >= 3

    _atomic_write(destination, data)
    return {"registered": True, "record": record}
