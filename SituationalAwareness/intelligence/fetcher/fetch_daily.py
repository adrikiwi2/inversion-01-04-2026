#!/usr/bin/env python3
"""
Daily Fetcher — Capa 1 del Intelligence Engine
Descarga datos de fuentes oficiales/públicas SIN LLM.
Output: data/daily_YYYY-MM-DD.json listo para enviar a Claude/Gemini para análisis.

Requisitos: pip install requests beautifulsoup4
APIs gratuitas usadas: Yahoo Finance v8, CoinGecko, Blockchain.com, FRED, CNN F&G
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

# ============================================================
# TICKERS
# ============================================================

CORE_SA_LP = [
    "CRWV", "BE", "TSEM", "LITE", "COHR", "INTC", "APLD",
    "CORZ", "RIOT", "HUT", "BTDR", "CLSK", "IREN", "BITF",
    "VST", "EQT", "LBRT", "GLXY", "GDX"
]

WATCHLIST = [
    "NVDA", "EQIX", "ETN", "VRT", "CEG", "OKLO", "SMR", "CCJ", "FCX", "ANET"
]

ETFS = [
    "SMH", "COPX", "URA", "GRID", "SRVR"
]

ALL_TICKERS = CORE_SA_LP + WATCHLIST + ETFS


# ============================================================
# FETCHERS
# ============================================================

def fetch_yahoo_quote(ticker: str) -> dict | None:
    """Yahoo Finance v8 chart endpoint — no auth needed."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    params = {"range": "5d", "interval": "1d", "includePrePost": "false"}
    try:
        r = requests.get(url, params=params, headers=UA, timeout=TIMEOUT)
        if r.status_code != 200:
            return {"ticker": ticker, "error": f"HTTP {r.status_code}"}
        data = r.json()
        result = data.get("chart", {}).get("result", [])
        if not result:
            return {"ticker": ticker, "error": "no data"}
        meta = result[0].get("meta", {})
        closes = result[0].get("indicators", {}).get("quote", [{}])[0].get("close", [])
        closes = [c for c in closes if c is not None]
        if len(closes) < 2:
            return {
                "ticker": ticker,
                "price": meta.get("regularMarketPrice"),
                "currency": meta.get("currency"),
                "change_1d": None,
                "change_1w": None,
            }
        price = closes[-1]
        prev = closes[-2]
        first = closes[0]
        return {
            "ticker": ticker,
            "price": round(price, 2),
            "currency": meta.get("currency", "USD"),
            "change_1d": f"{((price - prev) / prev) * 100:+.2f}%",
            "change_1w": f"{((price - first) / first) * 100:+.2f}%",
        }
    except Exception as e:
        return {"ticker": ticker, "error": str(e)}


def fetch_all_prices() -> list[dict]:
    """Fetch prices for all tickers with rate limiting."""
    results = []
    for i, ticker in enumerate(ALL_TICKERS):
        result = fetch_yahoo_quote(ticker)
        results.append(result)
        if i % 5 == 4:
            time.sleep(1)  # rate limit
    return results


def fetch_btc() -> dict:
    """BTC price via CoinGecko free API."""
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "bitcoin", "vs_currencies": "usd", "include_24hr_change": "true"},
            headers=UA, timeout=TIMEOUT
        )
        data = r.json().get("bitcoin", {})
        return {
            "btc_usd": data.get("usd"),
            "change_24h": f"{data.get('usd_24h_change', 0):+.2f}%",
        }
    except Exception as e:
        return {"error": str(e)}


def fetch_hashrate() -> dict:
    """BTC hashrate via Blockchain.com API."""
    try:
        r = requests.get(
            "https://api.blockchain.info/charts/hash-rate",
            params={"timespan": "14days", "format": "json"},
            headers=UA, timeout=TIMEOUT
        )
        data = r.json()
        values = data.get("values", [])
        if len(values) < 2:
            return {"error": "insufficient data"}
        current = values[-1]["y"]
        prev_day = values[-2]["y"]
        week_ago = values[-7]["y"] if len(values) >= 7 else values[0]["y"]
        return {
            "hashrate_ehs": round(current / 1e6, 2),  # convert to EH/s
            "change_1d": f"{((current - prev_day) / prev_day) * 100:+.2f}%",
            "change_1w": f"{((current - week_ago) / week_ago) * 100:+.2f}%",
        }
    except Exception as e:
        return {"error": str(e)}


def fetch_fear_greed() -> dict:
    """CNN Fear & Greed Index."""
    try:
        r = requests.get(
            "https://production.dataviz.cnn.io/index/fearandgreed/graphdata",
            headers={**UA, "Accept": "application/json"},
            timeout=TIMEOUT
        )
        data = r.json()
        fg = data.get("fear_and_greed", {})
        return {
            "score": round(fg.get("score", 0), 1),
            "rating": fg.get("rating", "unknown"),
            "previous_close": round(fg.get("previous_close", 0), 1),
        }
    except Exception as e:
        return {"error": str(e)}


def fetch_gold_kitco() -> dict:
    """Gold spot from Kitco (scrape fallback)."""
    try:
        r = requests.get(
            "https://proxy.kitco.com/getPM?symbol=AU&unit=USD&ounce=1",
            headers=UA, timeout=TIMEOUT
        )
        if r.status_code == 200:
            # Kitco sometimes returns XML or JSON depending on endpoint
            text = r.text
            return {"gold_raw_response": text[:500], "note": "parse manually or use LLM"}
    except:
        pass
    # Fallback: use Yahoo Finance gold futures
    result = fetch_yahoo_quote("GC=F")
    if result and result.get("price"):
        return {
            "gold_spot_usd": result["price"],
            "change_1d": result.get("change_1d"),
            "source": "Yahoo Finance GC=F"
        }
    return {"error": "could not fetch gold"}


def fetch_copper() -> dict:
    """Copper futures via Yahoo Finance."""
    result = fetch_yahoo_quote("HG=F")
    if result and result.get("price"):
        # HG=F is in USD/lb, convert to USD/ton (1 ton = 2204.62 lb)
        price_lb = result["price"]
        price_ton = round(price_lb * 2204.62, 2)
        return {
            "copper_usd_lb": price_lb,
            "copper_usd_ton": price_ton,
            "change_1d": result.get("change_1d"),
            "source": "Yahoo Finance HG=F"
        }
    return {"error": "could not fetch copper"}


def fetch_natgas() -> dict:
    """Natural gas Henry Hub via Yahoo Finance."""
    result = fetch_yahoo_quote("NG=F")
    if result and result.get("price"):
        return {
            "henry_hub_usd_mmbtu": result["price"],
            "change_1d": result.get("change_1d"),
            "source": "Yahoo Finance NG=F"
        }
    return {"error": "could not fetch natgas"}


def fetch_uranium_yahoo() -> dict:
    """Uranium proxy via URA ETF and Sprott trust (no free uranium spot API)."""
    ura = fetch_yahoo_quote("URA")
    sruuf = fetch_yahoo_quote("SRUUF")  # Sprott Physical Uranium Trust US OTC
    return {
        "ura_etf": ura,
        "sprott_uranium_trust": sruuf,
        "note": "Para spot real de uranio consultar numerco.com manualmente",
    }


def fetch_sec_edgar_rss() -> list[dict]:
    """Check SEC EDGAR full-text search for recent SA LP and CORZ filings."""
    filings = []
    searches = [
        ("Situational Awareness", "13F-HR,13D"),
        ("Core Scientific", "13D,8-K"),
    ]
    for query, forms in searches:
        try:
            url = "https://efts.sec.gov/LATEST/search-index"
            params = {"q": f'"{query}"', "forms": forms, "dateRange": "custom",
                      "startdt": TODAY, "enddt": TODAY}
            r = requests.get(url, params=params, headers={
                "User-Agent": "InvestmentResearch research@example.com",
                "Accept": "application/json"
            }, timeout=TIMEOUT)
            if r.status_code == 200:
                data = r.json()
                hits = data.get("hits", {}).get("hits", [])
                for hit in hits[:5]:
                    src = hit.get("_source", {})
                    filings.append({
                        "entity": src.get("entity_name"),
                        "form": src.get("form_type"),
                        "date": src.get("file_date"),
                        "description": src.get("display_name_no_content", ""),
                    })
        except Exception as e:
            filings.append({"query": query, "error": str(e)})
    return filings


def fetch_google_news_rss(query: str, max_items: int = 5) -> list[dict]:
    """Fetch headlines from Google News RSS."""
    try:
        from bs4 import BeautifulSoup
        url = f"https://news.google.com/rss/search?q={query}&hl=en&gl=US&ceid=US:en"
        r = requests.get(url, headers=UA, timeout=TIMEOUT)
        soup = BeautifulSoup(r.content, "xml")
        items = []
        for item in soup.find_all("item")[:max_items]:
            items.append({
                "title": item.title.text if item.title else "",
                "link": item.link.text if item.link else "",
                "pubDate": item.pubDate.text if item.pubDate else "",
                "source": item.source.text if item.source else "",
            })
        return items
    except ImportError:
        return [{"error": "beautifulsoup4 not installed, run: pip install beautifulsoup4"}]
    except Exception as e:
        return [{"error": str(e)}]


# ============================================================
# MAIN
# ============================================================

def main():
    print(f"[{TODAY}] Fetching daily intelligence data...")

    bundle = {
        "date": TODAY,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "prices": {},
        "commodities": {},
        "crypto": {},
        "macro": {},
        "sec_filings": [],
        "news": {},
        "alerts": [],
    }

    # 1. Prices
    print("  Fetching prices (34 tickers)...")
    all_prices = fetch_all_prices()
    for p in all_prices:
        ticker = p.get("ticker", "unknown")
        bundle["prices"][ticker] = p
        # Alert if >5% daily move
        change_str = p.get("change_1d", "0%")
        try:
            change_val = float(change_str.replace("%", "").replace("+", ""))
            if abs(change_val) >= 5:
                bundle["alerts"].append({
                    "ticker": ticker,
                    "move": change_str,
                    "timeframe": "1d",
                })
        except:
            pass

    # 2. Commodities
    print("  Fetching commodities...")
    bundle["commodities"]["copper"] = fetch_copper()
    time.sleep(1)
    bundle["commodities"]["gold"] = fetch_gold_kitco()
    time.sleep(1)
    bundle["commodities"]["natgas"] = fetch_natgas()
    time.sleep(1)
    bundle["commodities"]["uranium_proxy"] = fetch_uranium_yahoo()

    # 3. Crypto
    print("  Fetching BTC + hashrate...")
    bundle["crypto"]["btc"] = fetch_btc()
    bundle["crypto"]["hashrate"] = fetch_hashrate()

    # 4. Macro
    print("  Fetching Fear & Greed...")
    bundle["macro"]["fear_greed"] = fetch_fear_greed()

    # 5. SEC filings
    print("  Checking SEC EDGAR...")
    bundle["sec_filings"] = fetch_sec_edgar_rss()

    # 6. News (keyword-based RSS)
    print("  Fetching news RSS...")
    news_queries = {
        "power_crunch": '"data center" AND ("power crunch" OR "energy shortage" OR "grid capacity")',
        "nuclear_smr": '"NRC" AND ("SMR" OR "Oklo" OR "NuScale" OR "nuclear")',
        "btc_reconversion": '"Core Scientific" OR "CoreWeave" AND ("AI" OR "GPU" OR "data center")',
        "taiwan_china": '"Taiwan" AND ("China" OR "military" OR "blockade" OR "TSMC")',
        "uranium": '"uranium price" OR "uranium spot" OR "Kazatomprom"',
        "export_controls": '"export controls" AND ("semiconductor" OR "chips" OR "ASML")',
    }
    for key, query in news_queries.items():
        bundle["news"][key] = fetch_google_news_rss(query, max_items=3)
        time.sleep(0.5)

    # Save
    output_file = DATA_DIR / f"daily_{TODAY}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(bundle, f, indent=2, ensure_ascii=False)

    print(f"\n  Saved: {output_file}")
    print(f"  Alerts: {len(bundle['alerts'])}")
    print(f"  SEC filings today: {len(bundle['sec_filings'])}")
    total_news = sum(len(v) for v in bundle["news"].values())
    print(f"  News items: {total_news}")

    return bundle


if __name__ == "__main__":
    main()
