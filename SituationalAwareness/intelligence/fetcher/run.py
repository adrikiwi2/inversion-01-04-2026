#!/usr/bin/env python3
"""
Intelligence Engine — Orquestador CLI
Ejecuta fetch + análisis para cualquier frecuencia.

Uso:
  python run.py daily              # fetch diario + análisis con Codex
  python run.py weekly             # fetch semanal + análisis
  python run.py monthly            # fetch mensual + análisis
  python run.py quarterly          # fetch trimestral + análisis
  python run.py all                # ejecuta las 4 frecuencias
  python run.py fetch daily        # solo fetch, sin análisis
  python run.py analyze weekly     # solo análisis (bundle ya existente)
"""

import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")
PYTHON = sys.executable

FREQUENCIES = ["daily", "weekly", "monthly", "quarterly"]


def run_script(script: str, args: list[str] | None = None):
    """Run a Python script and stream output."""
    cmd = [PYTHON, str(HERE / script)] + (args or [])
    result = subprocess.run(cmd, cwd=str(HERE))
    return result.returncode


def run_fetch(freq: str) -> int:
    """Run the fetcher for a given frequency."""
    script = f"fetch_{freq}.py"
    if not (HERE / script).exists():
        print(f"  ERROR: {script} no existe")
        return 1
    return run_script(script)


def run_analyze(freq: str) -> int:
    """Run analysis for a given frequency."""
    script = "analyze_bundle.py"
    if not (HERE / script).exists():
        print(f"  ERROR: {script} no existe")
        return 1
    return run_script(script, [freq, TODAY])


def run_frequency(freq: str, fetch: bool = True, analyze: bool = True) -> int:
    """Run fetch + analyze for a frequency."""
    print(f"\n{'='*60}")
    print(f"  {freq.upper()} — {TODAY}")
    print(f"{'='*60}")

    if fetch:
        print(f"\n--- FETCH {freq} ---")
        rc = run_fetch(freq)
        if rc != 0:
            print(f"  Fetch {freq} failed (exit {rc})")
            return rc
        time.sleep(1)

    if analyze:
        print(f"\n--- ANALYZE {freq} ---")
        rc = run_analyze(freq)
        if rc != 0:
            print(f"  Analyze {freq} failed (exit {rc})")
            return rc

    return 0


def main():
    if len(sys.argv) < 2:
        print("Intelligence Engine — Orquestador CLI")
        print(f"Fecha: {TODAY}")
        print()
        print("Uso:")
        print("  python run.py daily          # fetch + analyze diario")
        print("  python run.py weekly         # fetch + analyze semanal")
        print("  python run.py monthly        # fetch + analyze mensual")
        print("  python run.py quarterly      # fetch + analyze trimestral")
        print("  python run.py all            # todas las frecuencias")
        print("  python run.py fetch daily    # solo fetch")
        print("  python run.py analyze daily  # solo analyze")
        sys.exit(0)

    cmd = sys.argv[1].lower()

    # Mode: fetch-only or analyze-only
    if cmd in ("fetch", "analyze"):
        if len(sys.argv) < 3:
            print(f"ERROR: especifica frecuencia: python run.py {cmd} <daily|weekly|monthly|quarterly>")
            sys.exit(1)
        freq = sys.argv[2].lower()
        if freq not in FREQUENCIES:
            print(f"ERROR: frecuencia '{freq}' no valida")
            sys.exit(1)
        rc = run_frequency(freq, fetch=(cmd == "fetch"), analyze=(cmd == "analyze"))
        sys.exit(rc)

    # Mode: full pipeline
    if cmd == "all":
        freqs = FREQUENCIES
    elif cmd in FREQUENCIES:
        freqs = [cmd]
    else:
        print(f"ERROR: comando '{cmd}' no reconocido")
        sys.exit(1)

    failed = []
    for freq in freqs:
        rc = run_frequency(freq)
        if rc != 0:
            failed.append(freq)

    print(f"\n{'='*60}")
    print(f"  RESUMEN")
    print(f"{'='*60}")
    print(f"  Ejecutados: {len(freqs)}")
    print(f"  OK: {len(freqs) - len(failed)}")
    if failed:
        print(f"  FAILED: {', '.join(failed)}")
    print(f"  Fecha: {TODAY}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
