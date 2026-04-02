# Weekly Intelligence Prompt

**Frecuencia:** Cada domingo o lunes antes de apertura
**Herramienta recomendada:** Perplexity (mejor para datos específicos) + Claude (para síntesis)
**Tiempo estimado:** 5-8 minutos

---

## Prompt 1: Bitcoin Hashrate y Reconversión

```
Fecha: {FECHA}

Analiza el estado actual de la reconversión de minería BTC a infraestructura de IA.

1. HASHRATE DE BITCOIN:
   - Hashrate total de la red Bitcoin (EH/s) — buscar en blockchain.com o similar
   - Variación semanal y mensual
   - Si hashrate baja mientras precio de BTC sube o se mantiene = señal de reconversión

2. DIFFICULTY ADJUSTMENT último:
   - ¿Subió o bajó? ¿Por cuánto?
   - Difficulty bajando = miners apagando máquinas (¿para reconvertir a IA?)

3. NOTICIAS DE RECONVERSIÓN esta semana:
   - ¿CORZ, RIOT, HUT, APLD, CLSK, IREN, WULF, BITF anunciaron algo?
   - Nuevos contratos de hosting GPU
   - Expansiones de capacidad de data center
   - Financiamientos o equity raises

4. PRECIO DE BITCOIN vs MINING ECONOMICS:
   - BTC price actual
   - Mining revenue per EH/s estimado
   - ¿Mining sigue siendo rentable o la reconversión a IA es más atractiva?

Formato JSON:
{
  "date": "YYYY-MM-DD",
  "btc_hashrate_ehs": X,
  "hashrate_change_1w": "+X%",
  "hashrate_change_1m": "+X%",
  "btc_price": X,
  "difficulty_last_adjustment": "+X%",
  "mining_revenue_per_eh": "$X/day",
  "reconversion_signal": "strong|moderate|weak|none",
  "reconversion_news": [
    {"company": "TICKER", "news": "descripción", "source": "url"}
  ],
  "thesis_note": "1 frase: ¿la reconversión BTC→IA se está acelerando o frenando?"
}
```

---

## Prompt 2: Short Interest y Sentimiento

```
Fecha: {FECHA}

Busca el short interest actual (% del float) para estos activos y compara con la semana anterior:

CORE SA LP:
CRWV, BE, CORZ, LITE, INTC, APLD, RIOT, HUT, CLSK, IREN

WATCHLIST:
NVDA, EQIX, VRT, OKLO, SMR, CCJ, FCX

Para cada uno reporta:
- Short interest (% of float)
- Days to cover
- Cambio vs semana anterior (subió/bajó)
- Si short interest > 15% → flag como "squeeze potential"
- Si short interest subió >3 puntos → flag como "bears building"

También busca:
- ¿Hay algún short seller report publicado esta semana sobre alguno de estos activos?
  (Hindenburg, Citron, Muddy Waters, etc.)

Formato JSON:
{
  "date": "YYYY-MM-DD",
  "short_interest": {
    "TICKER": {"si_pct": X, "days_cover": X, "change_1w": "+Xpp", "flag": "squeeze|bears|normal"}
  },
  "short_reports": [
    {"target": "TICKER", "author": "nombre", "date": "YYYY-MM-DD", "url": "url"}
  ]
}

Fuentes sugeridas: Finviz, MarketBeat, Ortex (si accesible), Yahoo Finance.
```

---

## Prompt 3: ETF Flows y Insider Trading

```
Fecha: {FECHA}

PARTE A — ETF FLOWS (última semana):
Busca flujos de capital (inflows/outflows) de estos ETFs:
SMH, SOXX, COPX, URA, URNM, GRID, SRVR, XLU, GDX, EWT

Para cada uno:
- Flow semanal ($M): positivo = inflows, negativo = outflows
- AUM actual
- Si hay inflow > $100M en la semana → flag "institutional interest"
- Si hay outflow > $50M → flag "rotation out"

Fuentes: ETF.com, ETFdb.com, Bloomberg (si accesible)

PARTE B — INSIDER TRADING (Form 4, última semana):
Busca insider buys/sells en SEC EDGAR para:
BE, CORZ, CRWV, LITE, APLD, VRT, OKLO, INTC

Para cada filing encontrado:
- Nombre del insider y cargo
- Buy o Sell
- Cantidad de acciones
- Valor en $
- Si CEO/CFO vende > $1M → flag "insider selling"
- Si múltiples insiders compran → flag "insider buying cluster"

Fuentes: SEC EDGAR Form 4, OpenInsider, Finviz insider

Formato JSON:
{
  "date": "YYYY-MM-DD",
  "etf_flows": {
    "TICKER": {"flow_1w_mm": X, "aum_mm": X, "flag": "institutional|rotation|normal"}
  },
  "insider_trades": [
    {
      "ticker": "X",
      "insider": "nombre",
      "title": "CEO|CFO|Director",
      "action": "buy|sell",
      "shares": X,
      "value_usd": X,
      "date": "YYYY-MM-DD",
      "flag": "selling|buying_cluster|normal"
    }
  ]
}
```
