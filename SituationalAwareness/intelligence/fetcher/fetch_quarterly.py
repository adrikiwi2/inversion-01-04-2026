#!/usr/bin/env python3
"""
Quarterly Fetcher — Capa 1 del Intelligence Engine
Ejecutar ~45 días después de cierre de trimestre (cuando salen 13F).
Output: data/quarterly_YYYY-MM-DD.json

Datos: 13F SA LP, 13D/A CORZ, earnings hiperscalers, holdings fundamentals,
       portfolio performance ranking.

Requisitos: pip install requests
"""

import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: pip install requests")
    sys.exit(1)

# Import full ticker list from daily fetcher
try:
    from fetch_daily import ALL_TICKERS
except ImportError:
    # Fallback if run from different working directory
    sys.path.insert(0, str(Path(__file__).parent))
    from fetch_daily import ALL_TICKERS

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) InvestmentResearch/1.0"}
EDGAR_UA = {"User-Agent": "InvestmentResearch research@example.com", "Accept": "application/json"}
TIMEOUT = 15

SA_LP_CIK = "0002045724"

# Hyperscaler tickers (demand signal)
HYPERSCALERS = ["GOOGL", "AMZN", "MSFT", "META", "NVDA"]

# Core SA LP holdings for fundamentals
CORE_HOLDINGS = ["BE", "CRWV", "CORZ", "LITE", "APLD", "TSEM", "VST", "EQT"]


def get_quarter_info() -> dict:
    """Determine current quarter and lookback period for filings."""
    now = datetime.now(timezone.utc)
    month = now.month
    year = now.year

    if month <= 3:
        current_q = f"Q1-{year}"
        # Look for Q3 filings from previous year (45-day delay)
        search_start = f"{year - 1}-10-01"
    elif month <= 6:
        current_q = f"Q2-{year}"
        search_start = f"{year}-01-01"
    elif month <= 9:
        current_q = f"Q3-{year}"
        search_start = f"{year}-04-01"
    else:
        current_q = f"Q4-{year}"
        search_start = f"{year}-07-01"

    return {
        "current_quarter": current_q,
        "search_start": search_start,
        "search_end": TODAY,
    }


# ============================================================
# SEC EDGAR FETCHERS
# ============================================================

def fetch_sa_lp_13f(q_info: dict) -> dict:
    """Search for SA LP 13F filings via EDGAR."""
    result = {
        "cik": SA_LP_CIK,
        "filings_found": [],
        "source": "SEC EDGAR",
    }

    # Method 1: Full-text search
    try:
        url = "https://efts.sec.gov/LATEST/search-index"
        params = {
            "q": '"Situational Awareness"',
            "forms": "13F-HR,13F-HR/A",
            "dateRange": "custom",
            "startdt": q_info["search_start"],
            "enddt": q_info["search_end"],
        }
        r = requests.get(url, params=params, headers=EDGAR_UA, timeout=TIMEOUT)
        if r.status_code == 200:
            data = r.json()
            hits = data.get("hits", {}).get("hits", [])
            for hit in hits[:10]:
                src = hit.get("_source", {})
                result["filings_found"].append({
                    "entity": src.get("entity_name"),
                    "form": src.get("form_type"),
                    "date": src.get("file_date"),
                    "description": src.get("display_name_no_content", ""),
                    "method": "full_text_search",
                })
    except Exception as e:
        result["search_error"] = str(e)

    time.sleep(1)

    # Method 2: Direct CIK lookup
    try:
        url = f"https://data.sec.gov/submissions/CIK{SA_LP_CIK}.json"
        r = requests.get(url, headers=EDGAR_UA, timeout=TIMEOUT)
        if r.status_code == 200:
            data = r.json()
            result["entity_name"] = data.get("name")
            result["entity_type"] = data.get("entityType")

            recent = data.get("filings", {}).get("recent", {})
            forms = recent.get("form", [])
            dates = recent.get("filingDate", [])
            accessions = recent.get("accessionNumber", [])
            descriptions = recent.get("primaryDocDescription", [])

            for i in range(min(len(forms), 20)):
                if "13F" in forms[i] or "13D" in forms[i]:
                    accession = accessions[i].replace("-", "") if i < len(accessions) else ""
                    filing_url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={SA_LP_CIK}&type={forms[i]}&dateb=&owner=include&count=10"
                    result["filings_found"].append({
                        "form": forms[i],
                        "date": dates[i] if i < len(dates) else None,
                        "accession": accessions[i] if i < len(accessions) else None,
                        "description": descriptions[i] if i < len(descriptions) else None,
                        "method": "cik_lookup",
                    })
    except Exception as e:
        result["cik_error"] = str(e)

    # Deduplicate by date+form
    seen = set()
    unique = []
    for f in result["filings_found"]:
        key = f"{f.get('form')}_{f.get('date')}"
        if key not in seen:
            seen.add(key)
            unique.append(f)
    result["filings_found"] = unique

    if unique:
        latest = max(unique, key=lambda x: x.get("date", ""))
        result["latest_filing_date"] = latest.get("date")
        result["latest_filing_type"] = latest.get("form")

    return result


def fetch_corz_13d(q_info: dict) -> dict:
    """Search for 13D/A filings on Core Scientific."""
    result = {"filings_found": []}

    try:
        url = "https://efts.sec.gov/LATEST/search-index"
        params = {
            "q": '"Core Scientific"',
            "forms": "SC 13D,SC 13D/A",
            "dateRange": "custom",
            "startdt": q_info["search_start"],
            "enddt": q_info["search_end"],
        }
        r = requests.get(url, params=params, headers=EDGAR_UA, timeout=TIMEOUT)
        if r.status_code == 200:
            data = r.json()
            hits = data.get("hits", {}).get("hits", [])
            for hit in hits[:10]:
                src = hit.get("_source", {})
                result["filings_found"].append({
                    "entity": src.get("entity_name"),
                    "form": src.get("form_type"),
                    "date": src.get("file_date"),
                    "description": src.get("display_name_no_content", ""),
                })
    except Exception as e:
        result["error"] = str(e)

    if result["filings_found"]:
        latest = max(result["filings_found"], key=lambda x: x.get("date", ""))
        result["latest_filing_date"] = latest.get("date")

    return result


# ============================================================
# YAHOO FINANCE FUNDAMENTALS
# ============================================================

def fetch_fundamentals(ticker: str) -> dict:
    """Fetch financial data from Yahoo Finance quoteSummary."""
    try:
        url = f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{ticker}"
        params = {"modules": "financialData,earningsTrend,defaultKeyStatistics"}
        r = requests.get(url, params=params, headers=UA, timeout=TIMEOUT)
        if r.status_code != 200:
            return {"ticker": ticker, "error": f"HTTP {r.status_code}"}

        data = r.json()
        results = data.get("quoteSummary", {}).get("result", [{}])[0]
        fin = results.get("financialData", {})
        stats = results.get("defaultKeyStatistics", {})

        def raw(d, key):
            v = d.get(key, {})
            return v.get("raw") if isinstance(v, dict) else v

        revenue = raw(fin, "totalRevenue")
        rev_growth = raw(fin, "revenueGrowth")
        earnings_growth = raw(fin, "earningsGrowth")
        profit_margin = raw(fin, "profitMargins")
        operating_margin = raw(fin, "operatingMargins")
        fcf = raw(fin, "freeCashflow")
        target_price = raw(fin, "targetMeanPrice")
        current_price = raw(fin, "currentPrice")
        rec = raw(fin, "recommendationMean")
        enterprise_value = raw(stats, "enterpriseValue")

        return {
            "ticker": ticker,
            "revenue_ttm": revenue,
            "revenue_growth": f"{rev_growth * 100:+.1f}%" if rev_growth else None,
            "earnings_growth": f"{earnings_growth * 100:+.1f}%" if earnings_growth else None,
            "profit_margin": f"{profit_margin * 100:.1f}%" if profit_margin else None,
            "operating_margin": f"{operating_margin * 100:.1f}%" if operating_margin else None,
            "free_cashflow": fcf,
            "enterprise_value": enterprise_value,
            "current_price": current_price,
            "target_price": target_price,
            "analyst_rating": rec,
        }
    except Exception as e:
        return {"ticker": ticker, "error": str(e)}


def fetch_capex(ticker: str) -> dict:
    """Fetch capex from cashflow statement."""
    try:
        url = f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{ticker}"
        params = {"modules": "cashflowStatementHistory"}
        r = requests.get(url, params=params, headers=UA, timeout=TIMEOUT)
        if r.status_code != 200:
            return {"error": f"HTTP {r.status_code}"}

        data = r.json()
        results = data.get("quoteSummary", {}).get("result", [{}])[0]
        statements = results.get("cashflowStatementHistory", {}).get("cashflowStatements", [])

        capex_data = []
        for stmt in statements[:4]:
            end_date = stmt.get("endDate", {}).get("fmt")
            capex_raw = stmt.get("capitalExpenditures", {})
            capex = capex_raw.get("raw") if isinstance(capex_raw, dict) else capex_raw
            capex_data.append({
                "period": end_date,
                "capex": capex,
            })

        return {"capex_history": capex_data}
    except Exception as e:
        return {"error": str(e)}


def fetch_hyperscaler_data() -> dict:
    """Fetch fundamentals + capex for hyperscalers."""
    results = {}
    for i, ticker in enumerate(HYPERSCALERS):
        fund = fetch_fundamentals(ticker)
        time.sleep(0.5)
        capex = fetch_capex(ticker)
        fund["capex"] = capex
        results[ticker] = fund

        # Alert: revenue growth < 5%
        rev_growth = fund.get("revenue_growth")
        if rev_growth:
            try:
                val = float(rev_growth.replace("%", "").replace("+", ""))
                if val < 5:
                    fund["alert"] = "revenue_growth_slowdown"
            except:
                pass

        if i % 3 == 2:
            time.sleep(1)

    return results


def fetch_holdings_data() -> dict:
    """Fetch fundamentals for core SA LP holdings."""
    results = {}
    for i, ticker in enumerate(CORE_HOLDINGS):
        results[ticker] = fetch_fundamentals(ticker)
        if i % 5 == 4:
            time.sleep(1)
        else:
            time.sleep(0.5)
    return results


# ============================================================
# PORTFOLIO PERFORMANCE
# ============================================================

def fetch_quarterly_return(ticker: str) -> dict:
    """Fetch 3-month return for a single ticker."""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        params = {"range": "3mo", "interval": "1d", "includePrePost": "false"}
        r = requests.get(url, params=params, headers=UA, timeout=TIMEOUT)
        if r.status_code != 200:
            return {"ticker": ticker, "error": f"HTTP {r.status_code}"}

        data = r.json()
        result = data.get("chart", {}).get("result", [])
        if not result:
            return {"ticker": ticker, "error": "no data"}

        closes = result[0].get("indicators", {}).get("quote", [{}])[0].get("close", [])
        closes = [c for c in closes if c is not None]
        if len(closes) < 2:
            return {"ticker": ticker, "error": "insufficient data"}

        first = closes[0]
        last = closes[-1]
        ret = ((last - first) / first) * 100

        return {
            "ticker": ticker,
            "price_start": round(first, 2),
            "price_end": round(last, 2),
            "return_3m": f"{ret:+.2f}%",
            "return_3m_raw": round(ret, 2),
        }
    except Exception as e:
        return {"ticker": ticker, "error": str(e)}


def fetch_portfolio_performance() -> dict:
    """Fetch 3mo performance for all tickers and rank."""
    all_returns = []

    for i, ticker in enumerate(ALL_TICKERS):
        ret = fetch_quarterly_return(ticker)
        all_returns.append(ret)
        if i % 5 == 4:
            time.sleep(1)

    # Filter valid returns
    valid = [r for r in all_returns if "return_3m_raw" in r]
    errors = [r for r in all_returns if "error" in r]

    # Sort
    valid.sort(key=lambda x: x["return_3m_raw"], reverse=True)

    top_gainers = valid[:10]
    top_losers = valid[-10:][::-1] if len(valid) >= 10 else valid[::-1]

    positive = len([r for r in valid if r["return_3m_raw"] > 0])
    negative = len([r for r in valid if r["return_3m_raw"] < 0])
    avg_return = sum(r["return_3m_raw"] for r in valid) / len(valid) if valid else 0

    return {
        "total_tickers": len(ALL_TICKERS),
        "successful": len(valid),
        "errors": len(errors),
        "positive": positive,
        "negative": negative,
        "avg_return": f"{avg_return:+.2f}%",
        "top_gainers": [{"ticker": r["ticker"], "return_3m": r["return_3m"]} for r in top_gainers],
        "top_losers": [{"ticker": r["ticker"], "return_3m": r["return_3m"]} for r in top_losers],
    }


# ============================================================
# MAIN
# ============================================================

def main():
    print(f"[{TODAY}] Fetching quarterly intelligence data...")

    q_info = get_quarter_info()
    print(f"  Quarter: {q_info['current_quarter']}")
    print(f"  Filing search window: {q_info['search_start']} -> {q_info['search_end']}")

    bundle = {
        "date": TODAY,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "quarter": q_info["current_quarter"],
        "sa_lp_13f": {},
        "corz_13d": {},
        "hyperscaler_fundamentals": {},
        "holdings_fundamentals": {},
        "portfolio_performance": {},
        "alerts": [],
    }

    # 1. SA LP 13F
    print("  Searching SEC EDGAR for SA LP 13F filings...")
    bundle["sa_lp_13f"] = fetch_sa_lp_13f(q_info)
    time.sleep(1)

    # 2. CORZ 13D/A
    print("  Searching SEC EDGAR for CORZ 13D/A filings...")
    bundle["corz_13d"] = fetch_corz_13d(q_info)
    time.sleep(1)

    # Alert: new 13F found
    if bundle["sa_lp_13f"].get("filings_found"):
        bundle["alerts"].append({
            "type": "sa_lp_13f_available",
            "latest_date": bundle["sa_lp_13f"].get("latest_filing_date"),
            "note": "New SA LP 13F filing detected — review positions",
        })

    # 3. Hyperscaler fundamentals
    print(f"  Fetching hyperscaler fundamentals ({len(HYPERSCALERS)} tickers)...")
    bundle["hyperscaler_fundamentals"] = fetch_hyperscaler_data()
    time.sleep(1)

    # Alert: any hyperscaler revenue slowdown
    for ticker, data in bundle["hyperscaler_fundamentals"].items():
        if data.get("alert") == "revenue_growth_slowdown":
            bundle["alerts"].append({
                "type": "hyperscaler_slowdown",
                "ticker": ticker,
                "revenue_growth": data.get("revenue_growth"),
                "note": f"{ticker} revenue growth <5% YoY — demand signal weakening?",
            })

    # 4. Holdings fundamentals
    print(f"  Fetching holdings fundamentals ({len(CORE_HOLDINGS)} tickers)...")
    bundle["holdings_fundamentals"] = fetch_holdings_data()
    time.sleep(1)

    # 5. Portfolio performance
    print(f"  Fetching quarterly performance ({len(ALL_TICKERS)} tickers)...")
    bundle["portfolio_performance"] = fetch_portfolio_performance()

    # Save
    output_file = DATA_DIR / f"quarterly_{TODAY}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(bundle, f, indent=2, ensure_ascii=False)

    print(f"\n  Saved: {output_file}")
    print(f"  Alerts: {len(bundle['alerts'])}")
    print(f"  SA LP 13F filings found: {len(bundle['sa_lp_13f'].get('filings_found', []))}")
    print(f"  CORZ 13D filings found: {len(bundle['corz_13d'].get('filings_found', []))}")
    perf = bundle["portfolio_performance"]
    print(f"  Portfolio: {perf.get('positive', 0)} up / {perf.get('negative', 0)} down, avg {perf.get('avg_return', 'N/A')}")

    return bundle


if __name__ == "__main__":
    main()
