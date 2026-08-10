"""Revertir de forma segura un plan de movimientos de auditoría de fechas.

Uso:
    python tools/rollback_date_audit_plan.py recovery/rollback_due_date_audit_20260809.json
    python tools/rollback_date_audit_plan.py recovery/rollback_due_date_audit_20260809.json --apply

Por defecto solo muestra una vista previa. Nunca sobrescribe un archivo existente.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Revierte movimientos de auditoría desde un plan JSON.")
    parser.add_argument("plan", type=Path, help="Ruta al archivo JSON de recuperación.")
    parser.add_argument("--apply", action="store_true", help="Aplica los movimientos; sin esta opción es vista previa.")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    data = json.loads(args.plan.read_text(encoding="utf-8"))
    moves = data.get("moves", [])

    print("\n" + "=" * 50)
    print("RECUPERACIÓN DE AUDITORÍA DE FECHAS")
    print("=" * 50)
    print(f"Movimientos del plan: {len(moves)}")
    print("Modo:", "APLICAR" if args.apply else "VISTA PREVIA")

    restored = 0
    skipped = 0

    for item in moves:
        current = Path(item["current_path"])
        original = Path(item["original_path"])

        print(f"\nActual:   {current}")
        print(f"Restaurar: {original}")

        if not current.exists():
            print("Estado: omitido; el archivo actual no existe.")
            skipped += 1
            continue
        if original.exists():
            print("Estado: omitido; el destino original ya existe. No se sobrescribe.")
            skipped += 1
            continue

        if not args.apply:
            print("Estado: would_restore")
            continue

        original.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(current), str(original))
        print("Estado: restored")
        restored += 1

    print("\n" + "=" * 50)
    if args.apply:
        print(f"Restaurados: {restored}")
        print(f"Omitidos: {skipped}")
    else:
        print("Vista previa completa; no se movió ningún archivo.")
    print("=" * 50)


if __name__ == "__main__":
    main()
