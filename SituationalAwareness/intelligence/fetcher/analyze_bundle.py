#!/usr/bin/env python3
"""
Analyze Bundle — Capa 2 del Intelligence Engine
Toma un JSON bundle de Capa 1 y lo envía a OpenAI Codex CLI (GPT-5.4) para análisis.
Gratis con ChatGPT Plus — sin coste de API.

Output: data/analysis_<freq>_<date>.json

Requisitos: npm i -g @openai/codex  (y estar logueado: codex --login)

Uso:
  python analyze_bundle.py daily              # analiza el bundle de hoy
  python analyze_bundle.py weekly
  python analyze_bundle.py monthly
  python analyze_bundle.py quarterly
  python analyze_bundle.py daily 2026-04-04   # bundle específico
"""

import json
import os
import subprocess
import sys
import shutil
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")

# Find codex binary
CODEX_BIN = shutil.which("codex") or shutil.which("codex.cmd")


# ============================================================
# PROMPT BUILDER
# ============================================================

SYSTEM_CONTEXT = """CONTEXTO: Eres un analista de inversiones senior monitorizando la tesis de Situational Awareness LP sobre infraestructura física de IA.
TESIS: "La infraestructura física (energía, data centers, conectividad) es el cuello de botella de la IA en 2026-2028. El valor migra a los dueños de los vatios."
SA LP: 19 posiciones core (CRWV, BE, TSEM, LITE, COHR, INTC, APLD, CORZ, RIOT, HUT, BTDR, CLSK, IREN, BITF, VST, EQT, LBRT, GLXY, GDX). Posición activista en CORZ (reconversión BTC a IA)."""

SCHEMAS = {
    "daily": {
        "focus": "Analiza movimientos >5%, noticias relevantes, commodities y Fear&Greed. Si F&G en extremos, comenta implicaciones.",
        "fields": "market_summary (2-3 frases), thesis_status (strengthening|stable|weakening), thesis_confidence (1-10), key_signals [{signal, direction, impact, tickers_affected, thesis_vector}], alerts_analysis [{ticker, move, probable_cause, action}], news_highlights [{headline, relevance, thesis_impact}], commodities_read {copper, gold, natgas, uranium}, fear_greed_read, action_items [], one_liner",
    },
    "weekly": {
        "focus": "Enfócate en reconversión BTC a IA. Mining margin negativo valida la tesis. Analiza short interest y insider activity.",
        "fields": "thesis_status, thesis_confidence, btc_reconversion_analysis {hashrate_trend, mining_profitability, reconversion_signal, reconversion_thesis, key_companies}, short_interest_analysis {notable_changes, squeeze_candidates, bears_building_on}, insider_activity {summary, notable_trades, signal}, etf_flows_read {institutional_interest, rotation_signal, thesis_impact}, action_items [], one_liner",
    },
    "monthly": {
        "focus": "Enfócate en si la infra física SIGUE siendo cuello de botella. Si lead times bajan o ocupación baja, tesis se debilita.",
        "fields": "thesis_status, thesis_confidence, commodities_analysis {copper, gold, natgas, uranium, lithium: {trend, thesis_read}, supercycle_verdict}, macro_read {cpi_implication, fed_funds_implication, industrial_production_read}, dc_infrastructure {occupancy_trend, lead_times_trend, interconnection_status, cooling_demand, bottleneck_verdict}, supercycle_score_read, action_items [], one_liner",
    },
    "quarterly": {
        "focus": "CRITICO: Si hiperscaler recorta capex >10% = RED FLAG. Analiza 13F SA LP, portfolio performance, y demand signal.",
        "fields": "thesis_status, thesis_confidence, sa_lp_portfolio_analysis {latest_13f_date, key_changes, thesis_evolution, conviction_level}, corz_activist_update {latest_13d_date, ownership_status, reconversion_progress}, hyperscaler_demand {aggregate_signal, capex_trend, red_flags, per_company}, portfolio_performance {summary, thesis_validated_by, thesis_challenged_by, rotation_opportunities}, quarterly_verdict, action_items [], one_liner",
    },
}


def build_prompt(freq: str, bundle_path: Path, output_path: Path, date: str) -> str:
    """Build a concise prompt for Codex."""
    schema = SCHEMAS[freq]

    # Read bundle and truncate if needed
    with open(bundle_path, "r", encoding="utf-8") as f:
        bundle = json.load(f)

    # Trim to keep prompt manageable for Codex
    bundle_str = json.dumps(bundle, ensure_ascii=False)
    if len(bundle_str) > 60000:
        # Trim news to 2 per category
        if "news" in bundle:
            for k in bundle["news"]:
                if isinstance(bundle["news"][k], list):
                    bundle["news"][k] = bundle["news"][k][:2]
        if "insider_trades" in bundle:
            bundle["insider_trades"] = bundle["insider_trades"][:10]
        bundle_str = json.dumps(bundle, ensure_ascii=False)

    quarter = bundle.get("quarter", "")

    prompt = f"""{SYSTEM_CONTEXT}

TAREA: Analiza el bundle {freq} del {date}. {schema['focus']}

DATOS ({freq}_{date}.json):
{bundle_str}

INSTRUCCION: Escribe un archivo JSON valido en {str(output_path).replace(chr(92), '/')} con estos campos:
analysis_type: "{freq}", date: "{date}", {f'quarter: "{quarter}", ' if quarter else ''}{schema['fields']}

El JSON debe ser valido y parseable. No incluyas markdown ni texto fuera del JSON."""

    return prompt


# ============================================================
# ANALYSIS ENGINE
# ============================================================

def analyze_with_codex(freq: str, bundle_path: Path, date: str) -> dict:
    """Run Codex exec to analyze the bundle."""
    output_path = DATA_DIR / f"analysis_{freq}_{date}.json"
    last_msg_path = DATA_DIR / f"_codex_last_{freq}.txt"

    prompt = build_prompt(freq, bundle_path, output_path, date)

    print(f"  Launching Codex exec (GPT-5.4, full-auto)...")
    print(f"  Bundle: {bundle_path.name} ({bundle_path.stat().st_size:,} bytes)")
    print(f"  Prompt length: {len(prompt):,} chars")

    try:
        result = subprocess.run(
            [
                CODEX_BIN, "exec",
                "--full-auto",
                "-C", str(bundle_path.parent.parent).replace("\\", "/"),
                "-o", str(last_msg_path).replace("\\", "/"),
                "-",  # read prompt from stdin
            ],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=300,
            encoding="utf-8",
            errors="replace",
        )

        print(f"  Codex exit code: {result.returncode}")
        if result.stderr:
            stderr_clean = result.stderr.encode("ascii", "replace").decode("ascii")
            stderr_lines = [l for l in stderr_clean.strip().split("\n") if l.strip() and "warn" not in l.lower()]
            if stderr_lines:
                print(f"  Codex stderr: {stderr_lines[0][:200]}")

    except subprocess.TimeoutExpired:
        print("  ERROR: Codex timeout (5 min)")
        return {"error": "timeout"}
    except FileNotFoundError:
        print("  ERROR: codex no encontrado")
        print("  Instala: npm i -g @openai/codex && codex --login")
        sys.exit(1)

    # Try to read output file (Codex should have written it)
    if output_path.exists():
        return _load_and_tag(output_path, freq)

    # Fallback: try parsing last message
    if last_msg_path.exists():
        with open(last_msg_path, "r", encoding="utf-8") as f:
            text = f.read()
        parsed = _try_parse_json(text)
        if parsed and "error" not in parsed:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(parsed, f, indent=2, ensure_ascii=False)
            return _load_and_tag(output_path, freq)

    # Fallback: try stdout
    if result and result.stdout:
        parsed = _try_parse_json(result.stdout)
        if parsed and "error" not in parsed:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(parsed, f, indent=2, ensure_ascii=False)
            return _load_and_tag(output_path, freq)

    return {"error": "Codex no generó output parseable", "stdout": (result.stdout or "")[:500]}


def _load_and_tag(path: Path, freq: str) -> dict:
    """Load JSON and add meta tag."""
    with open(path, "r", encoding="utf-8") as f:
        analysis = json.load(f)
    analysis["_meta"] = {
        "engine": "codex-cli",
        "model": "gpt-5.4",
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
        "cost": "$0 (ChatGPT Plus)",
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    return analysis


def _try_parse_json(text: str) -> dict | None:
    """Try multiple strategies to extract JSON from text."""
    # Direct parse
    try:
        return json.loads(text.strip())
    except (json.JSONDecodeError, ValueError):
        pass

    # Code block extraction
    for marker in ["```json", "```"]:
        if marker in text:
            try:
                start = text.index(marker) + len(marker)
                if marker == "```":
                    nl = text.index("\n", start)
                    start = nl + 1
                end = text.index("```", start)
                return json.loads(text[start:end].strip())
            except (ValueError, json.JSONDecodeError):
                pass

    # Brace extraction
    first = text.find("{")
    last = text.rfind("}")
    if first != -1 and last > first:
        try:
            return json.loads(text[first:last + 1])
        except json.JSONDecodeError:
            pass

    return None


# ============================================================
# MAIN
# ============================================================

def main():
    if len(sys.argv) < 2:
        print("Uso: python analyze_bundle.py <daily|weekly|monthly|quarterly> [YYYY-MM-DD]")
        print("")
        print("Usa OpenAI Codex CLI (gratis con ChatGPT Plus).")
        print("Requisito: npm i -g @openai/codex && codex --login")
        sys.exit(1)

    freq = sys.argv[1].lower()
    if freq not in SCHEMAS:
        print(f"ERROR: frecuencia '{freq}' no valida. Usa: daily, weekly, monthly, quarterly")
        sys.exit(1)

    if not CODEX_BIN:
        print("ERROR: codex CLI no encontrado en PATH")
        print("Instala: npm i -g @openai/codex")
        sys.exit(1)

    date = sys.argv[2] if len(sys.argv) > 2 else TODAY

    print(f"[{date}] Analyzing {freq} bundle with Codex...")

    # 1. Check bundle exists
    bundle_path = DATA_DIR / f"{freq}_{date}.json"
    if not bundle_path.exists():
        print(f"  ERROR: No existe {bundle_path}")
        print(f"  Ejecuta primero: python fetch_{freq}.py")
        sys.exit(1)

    # 2. Analyze
    analysis = analyze_with_codex(freq, bundle_path, date)

    # 3. Summary
    if "error" in analysis:
        print(f"\n  ERROR: {analysis['error']}")
        sys.exit(1)

    output_file = DATA_DIR / f"analysis_{freq}_{date}.json"
    print(f"\n  Saved: {output_file}")

    status = analysis.get("thesis_status", "?")
    confidence = analysis.get("thesis_confidence", "?")
    one_liner = analysis.get("one_liner", "")
    print(f"  Thesis: {status} (confidence: {confidence}/10)")
    print(f"  Summary: {one_liner}")

    actions = analysis.get("action_items", [])
    if actions:
        print("  Actions:")
        for a in actions:
            print(f"    - {a}")

    return analysis


if __name__ == "__main__":
    main()
