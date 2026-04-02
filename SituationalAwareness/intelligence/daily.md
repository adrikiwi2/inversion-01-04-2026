# Daily Intelligence Prompt

**Frecuencia:** Cada día de mercado (L-V)
**Herramienta recomendada:** Gemini (tiene Google Finance nativo) o Perplexity
**Tiempo estimado:** 2-3 minutos de ejecución

---

## Prompt 1: Precios y Commodities

```
Eres un analista de inversiones monitorizando la tesis de infraestructura física de IA.
Fecha de hoy: {FECHA}

Busca los precios de cierre de ayer (o último disponible) para TODOS estos activos y devuélvelos en formato JSON. Incluye variación diaria (%) y variación semanal (%).

ACCIONES CORE (portfolio SA LP):
CRWV, BE, TSEM, LITE, COHR, INTC, APLD, CORZ, RIOT, HUT, BTDR, CLSK, IREN, BITF, VST, EQT, LBRT, GLXY, GDX

ACCIONES WATCHLIST:
NVDA, EQIX, ETN, VRT, CEG, OKLO, SMR, CCJ, FCX, ANET

COMMODITIES Y FUTUROS:
- Cobre (LME spot, $/ton)
- Uranio spot (U3O8, $/lb) — buscar en Numerco o UxC
- Gas natural (Henry Hub, $/MMBtu)
- Oro (spot, $/oz)
- Bitcoin (BTC/USD)
- Electricidad PJM Western Hub (day-ahead, $/MWh) — si disponible

ETFs CLAVE:
SMH, COPX, URA, GRID, SRVR, CNDX (o CNDX.L)

Formato de respuesta (JSON):
{
  "date": "YYYY-MM-DD",
  "assets": {
    "TICKER": {"price": X, "change_1d": "+X.X%", "change_1w": "+X.X%"}
  },
  "commodities": {
    "copper_lme": {"price": X, "unit": "$/ton", "change_1d": "X%"},
    "uranium_spot": {"price": X, "unit": "$/lb", "change_1d": "X%"},
    "natgas_henry": {"price": X, "unit": "$/MMBtu", "change_1d": "X%"},
    "gold_spot": {"price": X, "unit": "$/oz", "change_1d": "X%"},
    "btc_usd": {"price": X, "change_1d": "X%"},
    "pjm_western": {"price": X, "unit": "$/MWh", "change_1d": "X%"}
  },
  "alerts": [
    // Solo si algún activo se movió >5% en el día o >10% en la semana
    {"ticker": "X", "move": "+X%", "timeframe": "1d", "note": "razón si conocida"}
  ]
}

NO inventes datos. Si no encuentras un precio, pon null y explica por qué.
```

---

## Prompt 2: Noticias y SEC Filings

```
Eres un analista de inversiones. Fecha: {FECHA}

Busca en la web las noticias de las últimas 24 horas relevantes para la tesis de inversión en infraestructura física de IA. Cubre TODOS estos vectores:

1. EARNINGS Y GUIDANCE: ¿Alguna de estas empresas reportó resultados o actualizó guidance?
   CRWV, BE, CORZ, EQIX, ETN, VRT, NVDA, INTC, TSMC, CEG, OKLO, CCJ

2. SEC FILINGS: Busca en EDGAR (sec.gov) si hay filings nuevos de:
   - Situational Awareness LP (CIK 0002045724) — 13F, 13D/A
   - Core Scientific (CORZ) — 13D/A, 8-K
   - CoreWeave (CRWV) — S-1, 10-Q, insider sales

3. M&A Y DEALS: ¿Alguna adquisición, fusión, partnership o contrato relevante?
   Especialmente: contratos PPA de energía nuclear/renovable con hiperscalers

4. REGULACIÓN:
   - NRC (Nuclear Regulatory Commission): aprobaciones SMR, Oklo, NuScale
   - BIS/Commerce: nuevos export controls a semiconductores
   - FERC: cambios en regulación de interconexión eléctrica
   - CHIPS Act: desembolsos, cambios

5. GEOPOLÍTICA:
   - Taiwán-China: tensión militar, sanciones, ejercicios
   - Rusia-Kazajistán: afecta suministro de uranio
   - Oriente Medio: afecta Tower Semiconductor (Israel)

Formato de respuesta (JSON):
{
  "date": "YYYY-MM-DD",
  "news": [
    {
      "headline": "texto",
      "source": "url o nombre",
      "category": "earnings|filing|deal|regulation|geopolitics|other",
      "tickers_affected": ["TICKER1", "TICKER2"],
      "thesis_impact": "bullish|bearish|neutral",
      "thesis_vector": "power|chips|connectivity|nuclear|btc_reconversion|macro",
      "summary": "1-2 frases de por qué importa para la tesis"
    }
  ],
  "sec_filings": [
    {
      "filer": "nombre",
      "type": "13F|13D|8-K|10-Q|S-1",
      "date": "YYYY-MM-DD",
      "url": "url de EDGAR",
      "summary": "qué dice"
    }
  ],
  "alert_level": "green|yellow|red"
  // green = nada relevante
  // yellow = algo que monitorizar
  // red = acción requerida (filing SA LP, geopolítica grave, earnings miss)
}

Busca en fuentes reales. NO inventes noticias. Si no hay nada relevante, di "Sin novedades" y pon alert_level: "green".
```

---

## Prompt 3: Señal de Power Crunch (específico de tesis)

```
Fecha: {FECHA}

Busca datos actualizados sobre el "power crunch" de centros de datos de IA en EE.UU.:

1. PRECIOS DE ELECTRICIDAD: ¿Hay datos recientes de precios spot en PJM, ERCOT, CAISO?
   ¿Algún spike inusual? ¿Forward prices subiendo?

2. COLAS DE INTERCONEXIÓN: ¿Alguna noticia sobre retrasos en permisos de conexión a red?
   ¿Tiempo medio de espera en PJM, ERCOT? ¿Algún cambio regulatorio de FERC?

3. ANUNCIOS DE DATA CENTERS: ¿Algún hiperscaler (Google, Amazon, Microsoft, Meta) anunció
   nuevo data center o expansión? ¿De cuántos MW? ¿Dónde?

4. RECONVERSIÓN BTC→IA: ¿Alguna minera de Bitcoin anunció reconversión de capacidad a IA?
   ¿Contratos nuevos con CoreWeave u otro proveedor de cloud GPU?

5. NUCLEAR/SMR: ¿Algún avance en despliegue de SMR? ¿Nuevo PPA nuclear?
   ¿Oklo, NuScale, Constellation, Rolls-Royce SMR?

Formato JSON:
{
  "date": "YYYY-MM-DD",
  "power_crunch_signals": [
    {
      "signal": "descripción",
      "source": "url",
      "direction": "tightening|easing",
      "impact": "high|medium|low",
      "tickers_affected": ["TICKER"]
    }
  ],
  "thesis_status": "strengthening|stable|weakening",
  "thesis_note": "1 frase resumen"
}
```
