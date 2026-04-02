# Quarterly Intelligence Prompt

**Frecuencia:** ~45 días después de cierre de trimestre (cuando salen 13F)
**Herramienta recomendada:** Perplexity + Claude para análisis de filings
**Tiempo estimado:** 15-20 minutos

---

## Prompt 1: 13F de Situational Awareness LP

```
Fecha: {FECHA}
Trimestre a analizar: {Q}

Busca el filing 13F más reciente de Situational Awareness LP (CIK 0002045724) en SEC EDGAR.
También busca en WhaleWisdom y Fintel para datos procesados.

EXTRAER:
1. VALOR TOTAL DEL PORTFOLIO y comparación con trimestre anterior
2. TODAS las posiciones (ticker, nombre, valor $, shares, % del portfolio)
3. CAMBIOS vs trimestre anterior:
   - Nuevas posiciones (NEW)
   - Posiciones incrementadas (UP) con % de incremento
   - Posiciones reducidas (DOWN) con % de reducción
   - Posiciones eliminadas (EXIT)
4. USO DE OPCIONES: ¿hay líneas de CALL o PUT? ¿Sobre qué subyacentes?
5. CONCENTRACIÓN: Top 10 como % del total
6. POSICIÓN EN CORZ: ¿cambió el 13D/A? ¿Más o menos acciones? ¿Nuevo %?

Formato JSON:
{
  "filing_date": "YYYY-MM-DD",
  "period": "YYYY-MM-DD",
  "total_value": X,
  "total_value_prev": X,
  "change_pct": "X%",
  "top_10_concentration_pct": X,
  "positions": [
    {
      "ticker": "X",
      "name": "X",
      "value_mm": X,
      "shares": X,
      "pct_portfolio": X,
      "change": "NEW|UP|DOWN|EXIT|FLAT",
      "change_detail": "descripción",
      "options": "CALL|PUT|none"
    }
  ],
  "corz_13d": {
    "shares": X,
    "pct_ownership": X,
    "change": "UP|DOWN|FLAT",
    "notes": "texto"
  },
  "key_rotations": "2-3 frases: ¿hacia dónde rota SA LP este trimestre?",
  "thesis_evolution": "¿La tesis sigue igual o está mutando? ¿Nuevos sectores?"
}
```

---

## Prompt 2: Earnings de Hiperscalers (Capex Guidance)

```
Fecha: {FECHA}
Trimestre: {Q}

Busca los resultados trimestrales más recientes de los 4 hiperscalers + NVIDIA.
Estos son los CLIENTES de la infraestructura de IA. Su capex guidance es LA señal de demanda.

EMPRESAS:
- Alphabet (GOOGL) — Google Cloud
- Amazon (AMZN) — AWS
- Microsoft (MSFT) — Azure
- Meta Platforms (META) — AI/Metaverse infra
- NVIDIA (NVDA) — GPU demand signal

Para CADA una extraer:
1. Revenue total y crecimiento YoY
2. Revenue del segmento cloud/AI específico
3. CAPEX del trimestre ($$) y variación YoY
4. CAPEX GUIDANCE para próximo trimestre/año — ESTO ES LO MÁS IMPORTANTE
5. Menciones en earnings call de:
   - "power" / "energy" / "electricity"
   - "data center" / "capacity constraints"
   - "nuclear" / "PPA"
   - "cooling" / "liquid cooling"
   - "supply chain" / "GPU supply"
6. ¿Alguno RECORTÓ capex guidance? → RED FLAG para toda la tesis

Formato JSON:
{
  "quarter": "Q-YYYY",
  "hyperscaler_capex": {
    "TICKER": {
      "revenue_b": X,
      "revenue_yoy": "X%",
      "cloud_revenue_b": X,
      "capex_b": X,
      "capex_yoy": "X%",
      "capex_guidance_next_q": X,
      "capex_guidance_fy": X,
      "capex_direction": "UP|FLAT|DOWN",
      "key_mentions": ["power constraints mentioned", "nuclear PPA signed", etc],
      "red_flag": true|false,
      "red_flag_detail": "texto si aplica"
    }
  },
  "aggregate_capex_b": X,
  "aggregate_capex_yoy": "X%",
  "demand_signal": "accelerating|stable|decelerating|contracting",
  "thesis_impact": "Si capex sigue subiendo, tesis de infraestructura se valida. Si recortan, re-evaluar.",
  "thesis_note": "2-3 frases"
}

CRÍTICO: Si CUALQUIER hiperscaler recorta capex guidance >10% vs anterior, eso es señal de que
la demanda de infraestructura puede frenar. Marcar como RED FLAG inmediato.
```

---

## Prompt 3: Earnings de Holdings Core SA LP

```
Fecha: {FECHA}
Trimestre: {Q}

Busca resultados trimestrales de los holdings core de Situational Awareness LP:

1. Bloom Energy (BE): revenue, backlog, margen, guidance
2. CoreWeave (CRWV): revenue, GPU utilization, nuevos contratos, cash burn
3. Core Scientific (CORZ): revenue minería vs hosting, MW reconvertidos, contratos GPU
4. Lumentum (LITE): revenue óptica, demand de transceivers 400G/800G
5. Applied Digital (APLD): revenue hosting, MW operativos, pipeline
6. Tower Semiconductor (TSEM): utilización de capacidad, nuevos clientes, nodos
7. Vistra Energy (VST): generación, precios de venta, margen
8. EQT Corporation (EQT): producción gas, precios realizados

Para cada uno:
- Revenue y variación YoY
- Métrica clave del negocio (backlog, MW, utilización, etc.)
- Guidance para próximo trimestre
- ¿Sorpresa positiva o negativa vs consenso?
- ¿Algún cambio de estrategia anunciado?

Formato JSON:
{
  "quarter": "Q-YYYY",
  "holdings": {
    "TICKER": {
      "revenue_mm": X,
      "revenue_yoy": "X%",
      "key_metric": {"name": "X", "value": X, "trend": "up|flat|down"},
      "guidance": "texto",
      "beat_miss": "beat|miss|inline",
      "strategy_change": "texto o null"
    }
  },
  "portfolio_health": "strong|mixed|weak",
  "thesis_note": "resumen"
}
```
