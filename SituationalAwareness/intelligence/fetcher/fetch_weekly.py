#!/usr/bin/env python3
"""
Weekly Fetcher — Capa 1 del Intelligence Engine
Ejecutar cada domingo o lunes antes de apertura.
Output: data/weekly_YYYY-MM-DD.json

Datos: hashrate BTC + difficulty, short interest, insider trading (Form 4),
       ETF volume activity, mining economics.

Requisitos: pip install requests beautifulsoup4
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: pip install requests beautifulsoup4")
    sys.exit(1)

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")
WEEK_AGO = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) InvestmentResearch/1.0"}
EDGAR_UA = {"User-Agent": "InvestmentResearch research@example.com", "Accept": "application/json"}
TIMEOUT = 15

# Tickers for short interest check
SI_TICKERS = [
    "CRWV", "BE", "CORZ", "LITE", "INTC", "APLD", "RIOT", "HUT",
    "CLSK", "IREN", "NVDA", "EQIX", "VRT", "OKLO", "SMR", "CCJ", "FCX",
]

# Tickers for insider trading (Form 4)
INSIDER_TICKERS = ["BE", "CORZ", "CRWV", "LITE", "APLD", "VRT", "OKLO", "INTC"]

# ETFs for volume activity
ETF_TICKERS = ["SMH", "SOXX", "COPX", "URA", "URNM", "GRID", "SRVR", "XLU", "GDX", "EWT"]


# ============================================================
# FETCHERS
# ============================================================

def fetch_hashrate_deep() -> dict:
    """BTC hashrate 30-day history + difficulty from Blockchain.com."""
    result = {}

    # Hashrate
    try:
        r = requests.get(
            "https://api.blockchain.info/charts/hash-rate",
            params={"timespan": "30days", "format": "json"},
            headers=UA, timeout=TIMEOUT
        )
        data = r.json()
        values = data.get("values", [])
        if len(values) >= 7:
            current = values[-1]["y"]
            week_ago = values[-7]["y"]
            month_ago = values[0]["y"]
            result["hashrate_ehs"] = round(current / 1e6, 2)
            result["hashrate_change_1w"] = f"{((current - week_ago) / week_ago) * 100:+.2f}%"
            result["hashrate_change_1m"] = f"{((current - month_ago) / month_ago) * 100:+.2f}%"
        else:
            result["hashrate_error"] = "insufficient data"
    except Exception as e:
        result["hashrate_error"] = str(e)

    time.sleep(1)

    # Difficulty
    try:
        r = requests.get(
            "https://api.blockchain.info/charts/difficulty",
            params={"timespan": "60days", "format": "json"},
            headers=UA, timeout=TIMEOUT
        )
        data = r.json()
        values = data.get("values", [])
        if len(values) >= 2:
            # Find the last difficulty change (value differs from previous)
            changes = []
            for i in range(1, len(values)):
                if values[i]["y"] != values[i - 1]["y"]:
                    pct = ((values[i]["y"] - values[i - 1]["y"]) / values[i - 1]["y"]) * 100
                    changes.append({"date": values[i]["x"], "change_pct": round(pct, 2)})
            if changes:
                last = changes[-1]
                result["difficulty_last_adjustment"] = f"{last['change_pct']:+.2f}%"
                result["difficulty_last_date"] = datetime.fromtimestamp(
                    last["date"], tz=timezone.utc
                ).strftime("%Y-%m-%d")
            else:
                result["difficulty_last_adjustment"] = "no change detected"
        else:
            result["difficulty_error"] = "insufficient data"
    except Exception as e:
        result["difficulty_error"] = str(e)

    return result


def fetch_btc_price() -> float | None:
    """BTC price from CoinGecko."""
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "bitcoin", "vs_currencies": "usd"},
            headers=UA, timeout=TIMEOUT
        )
        return r.json().get("bitcoin", {}).get("usd")
    except:
        return None


def calc_mining_economics(btc_price: float | None, hashrate_ehs: float | None) -> dict:
    """Estimate mining revenue per EH/s per day."""
    if not btc_price or not hashrate_ehs or hashrate_ehs == 0:
        return {"error": "missing data"}

    # Block reward = 3.125 BTC (post-2024 halving)
    # ~144 blocks/day
    block_reward = 3.125
    blocks_per_day = 144
    daily_btc_mined = block_reward * blocks_per_day  # 450 BTC/day
    revenue_per_eh = (daily_btc_mined / hashrate_ehs) * btc_price

    # Rough electricity cost estimate: ~30 MW per EH/s, $0.05/kWh
    power_per_eh_mw = 30
    hours_per_day = 24
    cost_per_kwh = 0.05
    daily_elec_cost = power_per_eh_mw * 1000 * hours_per_day * cost_per_kwh  # $36,000

    profit = revenue_per_eh - daily_elec_cost

    # Reconversion signal: if mining profit margin < 20%, AI hosting is more attractive
    margin = (profit / revenue_per_eh * 100) if revenue_per_eh > 0 else 0

    if margin < 0:
        signal = "strong"
    elif margin < 20:
        signal = "moderate"
    elif margin < 40:
        signal = "weak"
    else:
        signal = "none"

    return {
        "btc_price": btc_price,
        "daily_btc_mined": daily_btc_mined,
        "revenue_per_eh_day_usd": round(revenue_per_eh, 2),
        "est_electricity_cost_per_eh_day_usd": round(daily_elec_cost, 2),
        "est_profit_per_eh_day_usd": round(profit, 2),
        "est_margin_pct": round(margin, 1),
        "reconversion_signal": signal,
    }


def fetch_short_interest(ticker: str) -> dict:
    """Short interest via Yahoo Finance quoteSummary."""
    try:
        url = f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{ticker}"
        params = {"modules": "defaultKeyStatistics"}
        r = requests.get(url, params=params, headers=UA, timeout=TIMEOUT)
        if r.status_code != 200:
            return {"ticker": ticker, "error": f"HTTP {r.status_code}"}
        data = r.json()
        stats = data.get("quoteSummary", {}).get("result", [{}])[0].get("defaultKeyStatistics", {})

        si_pct_raw = stats.get("shortPercentOfFloat", {})
        si_pct = si_pct_raw.get("raw") if isinstance(si_pct_raw, dict) else si_pct_raw
        si_pct = round(si_pct * 100, 2) if si_pct and si_pct < 1 else si_pct  # convert decimal to %

        short_ratio_raw = stats.get("shortRatio", {})
        short_ratio = short_ratio_raw.get("raw") if isinstance(short_ratio_raw, dict) else short_ratio_raw

        shares_short_raw = stats.get("sharesShort", {})
        shares_short = shares_short_raw.get("raw") if isinstance(shares_short_raw, dict) else shares_short_raw

        flag = "normal"
        if si_pct and si_pct > 15:
            flag = "squeeze_potential"

        return {
            "ticker": ticker,
            "si_pct": si_pct,
            "short_ratio": round(short_ratio, 2) if short_ratio else None,
            "shares_short": shares_short,
            "flag": flag,
        }
    except Exception as e:
        return {"ticker": ticker, "error": str(e)}


def fetch_all_short_interest() -> dict:
    """Fetch short interest for all monitored tickers."""
    results = {}
    for i, ticker in enumerate(SI_TICKERS):
        results[ticker] = fetch_short_interest(ticker)
        if i % 5 == 4:
            time.sleep(1)
    return results


def fetch_insider_trades() -> list[dict]:
    """Check SEC EDGAR Form 4 filings for insider trades."""
    trades = []
    for company in INSIDER_TICKERS:
        try:
            url = "https://efts.sec.gov/LATEST/search-index"
            params = {
                "q": f'"{company}"',
                "forms": "4",
                "dateRange": "custom",
                "startdt": WEEK_AGO,
                "enddt": TODAY,
            }
            r = requests.get(url, params=params, headers=EDGAR_UA, timeout=TIMEOUT)
            if r.status_code == 200:
                data = r.json()
                hits = data.get("hits", {}).get("hits", [])
                for hit in hits[:5]:
                    src = hit.get("_source", {})
                    trades.append({
                        "ticker": company,
                        "entity": src.get("entity_name"),
                        "form": src.get("form_type"),
                        "date": src.get("file_date"),
                        "description": src.get("display_name_no_content", ""),
                    })
        except Exception as e:
            trades.append({"ticker": company, "error": str(e)})
        time.sleep(0.5)
    return trades


def fetch_etf_volume(ticker: str) -> dict:
    """Fetch 5d and 20d volume for an ETF to detect flow anomalies."""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        params = {"range": "1mo", "interval": "1d", "includePrePost": "false"}
        r = requests.get(url, params=params, headers=UA, timeout=TIMEOUT)
        if r.status_code != 200:
            return {"ticker": ticker, "error": f"HTTP {r.status_code}"}
        data = r.json()
        result = data.get("chart", {}).get("result", [])
        if not result:
            return {"ticker": ticker, "error": "no data"}
        volumes = result[0].get("indicators", {}).get("quote", [{}])[0].get("volume", [])
        volumes = [v for v in volumes if v is not None and v > 0]
        if len(volumes) < 5:
            return {"ticker": ticker, "error": "insufficient volume data"}

        avg_5d = sum(volumes[-5:]) / 5
        avg_20d = sum(volumes) / len(volumes)
        ratio = avg_5d / avg_20d if avg_20d > 0 else 0

        flag = "high_activity" if ratio > 1.5 else "normal"

        return {
            "ticker": ticker,
            "avg_vol_5d": int(avg_5d),
            "avg_vol_20d": int(avg_20d),
            "ratio": round(ratio, 2),
            "flag": flag,
        }
    except Exception as e:
        return {"ticker": ticker, "error": str(e)}


def fetch_all_etf_activity() -> dict:
    """Fetch volume activity for all ETFs."""
    results = {}
    for i, ticker in enumerate(ETF_TICKERS):
        results[ticker] = fetch_etf_volume(ticker)
        if i % 5 == 4:
            time.sleep(1)
    return results


# ============================================================
# MAIN
# ============================================================

def main():
    print(f"[{TODAY}] Fetching weekly intelligence data...")

    bundle = {
        "date": TODAY,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "btc_mining": {},
        "short_interest": {},
        "insider_trades": [],
        "etf_activity": {},
        "alerts": [],
    }

    # 1. BTC hashrate + difficulty
    print("  Fetching BTC hashrate & difficulty (30d + 60d)...")
    hashrate_data = fetch_hashrate_deep()
    time.sleep(1)

    # 2. BTC price + mining economics
    print("  Fetching BTC price & mining economics...")
    btc_price = fetch_btc_price()
    hashrate_ehs = hashrate_data.get("hashrate_ehs")
    mining_econ = calc_mining_economics(btc_price, hashrate_ehs)

    bundle["btc_mining"] = {**hashrate_data, **mining_econ}
    time.sleep(1)

    # Alert on reconversion signal
    if mining_econ.get("reconversion_signal") in ("strong", "moderate"):
        bundle["alerts"].append({
            "type": "reconversion_signal",
            "signal": mining_econ["reconversion_signal"],
            "margin": mining_econ.get("est_margin_pct"),
            "note": "Mining margins compressing — reconversion to AI more attractive",
        })

    # 3. Short interest
    print(f"  Fetching short interest ({len(SI_TICKERS)} tickers)...")
    bundle["short_interest"] = fetch_all_short_interest()

    # Alert on squeeze potential
    for ticker, si_data in bundle["short_interest"].items():
        if si_data.get("flag") == "squeeze_potential":
            bundle["alerts"].append({
                "type": "short_squeeze_potential",
                "ticker": ticker,
                "si_pct": si_data.get("si_pct"),
            })
    time.sleep(1)

    # 4. Insider trading
    print(f"  Checking SEC EDGAR Form 4 ({len(INSIDER_TICKERS)} companies)...")
    bundle["insider_trades"] = fetch_insider_trades()
    time.sleep(1)

    # 5. ETF volume activity
    print(f"  Fetching ETF volume activity ({len(ETF_TICKERS)} ETFs)...")
    bundle["etf_activity"] = fetch_all_etf_activity()

    # Alert on high activity ETFs
    for ticker, etf_data in bundle["etf_activity"].items():
        if etf_data.get("flag") == "high_activity":
            bundle["alerts"].append({
                "type": "etf_high_activity",
                "ticker": ticker,
                "ratio": etf_data.get("ratio"),
                "note": f"5d avg volume {etf_data.get('ratio', 0):.1f}x above 20d avg",
            })

    # Save
    output_file = DATA_DIR / f"weekly_{TODAY}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(bundle, f, indent=2, ensure_ascii=False)

    print(f"\n  Saved: {output_file}")
    print(f"  Alerts: {len(bundle['alerts'])}")
    print(f"  Short interest tickers: {len(bundle['short_interest'])}")
    print(f"  Insider filings found: {len(bundle['insider_trades'])}")
    print(f"  ETFs checked: {len(bundle['etf_activity'])}")

    return bundle


if __name__ == "__main__":
    main()
