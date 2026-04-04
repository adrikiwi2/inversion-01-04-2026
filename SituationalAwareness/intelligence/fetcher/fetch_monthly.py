#!/usr/bin/env python3
"""
Monthly Fetcher — Capa 1 del Intelligence Engine
Ejecutar el primer lunes de cada mes.
Output: data/monthly_YYYY-MM-DD.json

Datos: commodities deep (3mo history), PJM queue, FRED macro, DC news, superciclo.

Requisitos: pip install requests beautifulsoup4
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: pip install requests beautifulsoup4")
    sys.exit(1)

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) InvestmentResearch/1.0"}
TIMEOUT = 15

FRED_API_KEY = os.environ.get("FRED_API_KEY", "DEMO_KEY")

# Supercycle ETFs to track
SUPERCYCLE_ETFS = ["COPX", "URA", "REMX", "FIW", "XLU"]


# ============================================================
# YAHOO HELPERS
# ============================================================

def yahoo_history(ticker: str, range_str: str = "3mo") -> dict:
    """Fetch price history from Yahoo Finance. Returns first, last, high, low, changes."""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        params = {"range": range_str, "interval": "1d", "includePrePost": "false"}
        r = requests.get(url, params=params, headers=UA, timeout=TIMEOUT)
        if r.status_code != 200:
            return {"ticker": ticker, "error": f"HTTP {r.status_code}"}
        data = r.json()
        result = data.get("chart", {}).get("result", [])
        if not result:
            return {"ticker": ticker, "error": "no data"}

        meta = result[0].get("meta", {})
        closes = result[0].get("indicators", {}).get("quote", [{}])[0].get("close", [])
        highs = result[0].get("indicators", {}).get("quote", [{}])[0].get("high", [])
        lows = result[0].get("indicators", {}).get("quote", [{}])[0].get("low", [])

        closes = [c for c in closes if c is not None]
        highs = [h for h in highs if h is not None]
        lows = [lo for lo in lows if lo is not None]

        if len(closes) < 2:
            return {"ticker": ticker, "error": "insufficient data"}

        price = closes[-1]
        first = closes[0]
        high_52w = meta.get("fiftyTwoWeekHigh")
        low_52w = meta.get("fiftyTwoWeekLow")

        # 1mo change: ~21 trading days
        month_idx = max(0, len(closes) - 22)
        month_price = closes[month_idx]

        return {
            "ticker": ticker,
            "price": round(price, 2),
            "currency": meta.get("currency", "USD"),
            "change_period": f"{((price - first) / first) * 100:+.2f}%",
            "change_1m": f"{((price - month_price) / month_price) * 100:+.2f}%" if month_price else None,
            "high_period": round(max(highs), 2) if highs else None,
            "low_period": round(min(lows), 2) if lows else None,
            "high_52w": round(high_52w, 2) if high_52w else None,
            "low_52w": round(low_52w, 2) if low_52w else None,
        }
    except Exception as e:
        return {"ticker": ticker, "error": str(e)}


# ============================================================
# COMMODITIES DEEP
# ============================================================

def fetch_commodities_deep() -> dict:
    """Fetch 3-month history for key commodities."""
    results = {}

    # Copper (HG=F)
    copper = yahoo_history("HG=F", "3mo")
    if copper.get("price"):
        copper["unit"] = "$/lb"
        copper["price_per_ton"] = round(copper["price"] * 2204.62, 2)
    results["copper"] = copper
    time.sleep(1)

    # Gold (GC=F)
    gold = yahoo_history("GC=F", "3mo")
    if gold.get("price"):
        gold["unit"] = "$/oz"
    results["gold"] = gold
    time.sleep(1)

    # Natural gas (NG=F)
    natgas = yahoo_history("NG=F", "3mo")
    if natgas.get("price"):
        natgas["unit"] = "$/MMBtu"
    results["natgas"] = natgas
    time.sleep(1)

    # Uranium proxy (URA ETF + Sprott trust)
    ura = yahoo_history("URA", "3mo")
    sruuf = yahoo_history("SRUUF", "3mo")
    results["uranium_proxy"] = {
        "ura_etf": ura,
        "sprott_trust": sruuf,
        "note": "Para spot real consultar numerco.com",
    }
    time.sleep(1)

    # Lithium proxy (ALB + LIT ETF)
    alb = yahoo_history("ALB", "3mo")
    lit = yahoo_history("LIT", "3mo")
    results["lithium_proxy"] = {
        "albemarle": alb,
        "lit_etf": lit,
    }
    time.sleep(1)

    # Rare earths proxy (MP + REMX)
    mp = yahoo_history("MP", "3mo")
    remx = yahoo_history("REMX", "3mo")
    results["rare_earths_proxy"] = {
        "mp_materials": mp,
        "remx_etf": remx,
    }

    return results


# ============================================================
# PJM INTERCONNECTION QUEUE
# ============================================================

def fetch_pjm_queue() -> dict:
    """Try to get PJM queue data; fallback to news RSS."""
    result = {"data_available": False, "source": "Google News RSS fallback"}

    # PJM publishes queue data as Excel/CSV — we can't easily parse it,
    # so we use news as a proxy for queue status
    try:
        from bs4 import BeautifulSoup
        query = '"PJM interconnection queue" OR "PJM queue" OR "interconnection backlog GW"'
        url = f"https://news.google.com/rss/search?q={query}&hl=en&gl=US&ceid=US:en"
        r = requests.get(url, headers=UA, timeout=TIMEOUT)
        soup = BeautifulSoup(r.content, "xml")
        items = []
        for item in soup.find_all("item")[:5]:
            items.append({
                "title": item.title.text if item.title else "",
                "link": item.link.text if item.link else "",
                "pubDate": item.pubDate.text if item.pubDate else "",
                "source": item.source.text if item.source else "",
            })
        result["news"] = items
        if items:
            result["data_available"] = True
    except Exception as e:
        result["error"] = str(e)

    return result


# ============================================================
# FRED MACRO
# ============================================================

def fetch_fred_series(series_id: str, limit: int = 3) -> dict:
    """Fetch latest observations from FRED."""
    try:
        url = "https://api.stlouisfed.org/fred/series/observations"
        params = {
            "series_id": series_id,
            "api_key": FRED_API_KEY,
            "file_type": "json",
            "sort_order": "desc",
            "limit": limit,
        }
        r = requests.get(url, params=params, headers=UA, timeout=TIMEOUT)
        if r.status_code != 200:
            return {"series": series_id, "error": f"HTTP {r.status_code}"}
        data = r.json()
        obs = data.get("observations", [])
        if not obs:
            return {"series": series_id, "error": "no observations"}

        latest = obs[0]
        prior = obs[1] if len(obs) > 1 else None

        result = {
            "series": series_id,
            "value": latest.get("value"),
            "date": latest.get("date"),
        }
        if prior and latest.get("value") != "." and prior.get("value") != ".":
            try:
                curr = float(latest["value"])
                prev = float(prior["value"])
                result["prior_value"] = prior["value"]
                result["prior_date"] = prior["date"]
                result["change"] = f"{((curr - prev) / prev) * 100:+.2f}%" if prev != 0 else None
            except ValueError:
                pass
        return result
    except Exception as e:
        return {"series": series_id, "error": str(e)}


def fetch_all_macro() -> dict:
    """Fetch CPI, Fed Funds, Industrial Production from FRED."""
    results = {}

    results["cpi"] = fetch_fred_series("CPIAUCSL")
    time.sleep(0.5)
    results["fed_funds"] = fetch_fred_series("FEDFUNDS")
    time.sleep(0.5)
    results["industrial_production"] = fetch_fred_series("INDPRO")

    return results


# ============================================================
# DATA CENTER NEWS
# ============================================================

def fetch_dc_news() -> dict:
    """Fetch DC-related news across 4 categories."""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return {"error": "beautifulsoup4 not installed"}

    categories = {
        "occupancy": '"data center" AND ("occupancy" OR "vacancy" OR "colocation pricing")',
        "equipment_lead_times": '"transformer" AND ("lead time" OR "backlog" OR "shortage")',
        "ferc_interconnection": '"FERC" AND ("interconnection" OR "queue" OR "reform")',
        "liquid_cooling": '"liquid cooling" AND ("data center" OR "Vertiv" OR "CoolIT")',
    }

    results = {}
    for key, query in categories.items():
        try:
            url = f"https://news.google.com/rss/search?q={query}&hl=en&gl=US&ceid=US:en"
            r = requests.get(url, headers=UA, timeout=TIMEOUT)
            soup = BeautifulSoup(r.content, "xml")
            items = []
            for item in soup.find_all("item")[:5]:
                items.append({
                    "title": item.title.text if item.title else "",
                    "link": item.link.text if item.link else "",
                    "pubDate": item.pubDate.text if item.pubDate else "",
                    "source": item.source.text if item.source else "",
                })
            results[key] = items
        except Exception as e:
            results[key] = [{"error": str(e)}]
        time.sleep(0.5)

    return results


# ============================================================
# SUPERCYCLE SCORE
# ============================================================

def fetch_supercycle() -> dict:
    """Fetch 3mo and YTD performance of supercycle ETFs."""
    results = {}
    up_count = 0

    for i, ticker in enumerate(SUPERCYCLE_ETFS):
        data_3m = yahoo_history(ticker, "3mo")
        time.sleep(0.5)
        data_ytd = yahoo_history(ticker, "ytd")

        entry = {"ticker": ticker}
        if data_3m.get("price"):
            entry["price"] = data_3m["price"]
            entry["change_3m"] = data_3m.get("change_period")
            # Check if 3mo return > 5%
            try:
                chg = float(data_3m["change_period"].replace("%", "").replace("+", ""))
                if chg > 5:
                    up_count += 1
            except:
                pass
        if data_ytd.get("price"):
            entry["change_ytd"] = data_ytd.get("change_period")
        if data_3m.get("change_1m"):
            entry["change_1m"] = data_3m["change_1m"]

        results[ticker] = entry

        if i % 3 == 2:
            time.sleep(1)

    # Score and status
    score = f"{up_count}/{len(SUPERCYCLE_ETFS)} ETFs up >5% in 3mo"
    if up_count >= 4:
        status = "accelerating"
    elif up_count >= 2:
        status = "stable"
    else:
        status = "decelerating"

    results["supercycle_score"] = score
    results["status"] = status

    return results


# ============================================================
# MAIN
# ============================================================

def main():
    print(f"[{TODAY}] Fetching monthly intelligence data...")

    bundle = {
        "date": TODAY,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "commodities_deep": {},
        "pjm_queue": {},
        "macro": {},
        "dc_news": {},
        "supercycle": {},
        "alerts": [],
    }

    # 1. Commodities deep
    print("  Fetching commodities deep dive (3mo history)...")
    bundle["commodities_deep"] = fetch_commodities_deep()
    time.sleep(1)

    # 2. PJM queue
    print("  Checking PJM interconnection queue...")
    bundle["pjm_queue"] = fetch_pjm_queue()
    time.sleep(1)

    # 3. FRED macro
    print("  Fetching FRED macro data (CPI, Fed Funds, Industrial Production)...")
    bundle["macro"] = fetch_all_macro()
    time.sleep(1)

    # 4. DC news
    print("  Fetching data center news (4 categories)...")
    bundle["dc_news"] = fetch_dc_news()
    time.sleep(1)

    # 5. Supercycle
    print(f"  Fetching supercycle indicators ({len(SUPERCYCLE_ETFS)} ETFs)...")
    bundle["supercycle"] = fetch_supercycle()

    # Alerts
    # Supercycle decelerating
    if bundle["supercycle"].get("status") == "decelerating":
        bundle["alerts"].append({
            "type": "supercycle_decelerating",
            "score": bundle["supercycle"].get("supercycle_score"),
            "note": "Fewer than 2 commodity ETFs up >5% in 3mo",
        })

    # Copper spike (>10% in 3mo)
    copper = bundle["commodities_deep"].get("copper", {})
    if copper.get("change_period"):
        try:
            chg = float(copper["change_period"].replace("%", "").replace("+", ""))
            if chg > 10:
                bundle["alerts"].append({
                    "type": "copper_spike",
                    "change_3m": copper["change_period"],
                    "note": "Copper up >10% in 3mo — supply crunch signal",
                })
        except:
            pass

    # Save
    output_file = DATA_DIR / f"monthly_{TODAY}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(bundle, f, indent=2, ensure_ascii=False)

    print(f"\n  Saved: {output_file}")
    print(f"  Alerts: {len(bundle['alerts'])}")
    print(f"  Supercycle: {bundle['supercycle'].get('status', 'unknown')}")
    total_news = sum(len(v) for v in bundle.get("dc_news", {}).values() if isinstance(v, list))
    print(f"  DC news items: {total_news}")

    return bundle


if __name__ == "__main__":
    main()
