# Monthly Intelligence Prompt

**Frecuencia:** Primer lunes de cada mes
**Herramienta recomendada:** Perplexity (datos específicos de industria) + Claude (síntesis)
**Tiempo estimado:** 10-15 minutos

---

## Prompt 1: Estado de Data Centers y Ocupación

```
Fecha: {FECHA}

Busca los datos más recientes sobre el mercado de data centers en EE.UU. y Europa:

1. TASAS DE OCUPACIÓN por mercado clave:
   - Northern Virginia (Ashburn)
   - Dallas/Fort Worth
   - Phoenix/Mesa
   - Chicago
   - Londres
   - Frankfurt
   - Ámsterdam
   Fuentes: reportes de CBRE, JLL, Cushman & Wakefield, DatacenterHawk

2. NUEVA CAPACIDAD EN CONSTRUCCIÓN:
   - MW totales en construcción por mercado
   - Fecha estimada de entrega
   - ¿Algún proyecto retrasado por falta de energía?

3. PRECIOS DE COLOCATION:
   - $/kW/mes promedio en los mercados clave
   - Tendencia: subiendo, estable, bajando
   - ¿Premium por racks de alta densidad (>30kW)?

4. LEAD TIMES DE EQUIPAMIENTO:
   - Transformadores de potencia: meses de espera
   - Switchgear (Eaton, Schneider): meses de espera
   - Generadores de respaldo: meses de espera
   - Sistemas de refrigeración líquida (Vertiv): meses de espera
   Fuentes: reportes de fabricantes, noticias de industria, T&D World

5. PERMISOS DE INTERCONEXIÓN (FERC/ISOs):
   - Queue de PJM Interconnection: GW en espera
   - Tiempo medio de aprobación
   - ¿Algún cambio regulatorio de FERC este mes?
   Fuentes: PJM.com queue reports, FERC orders

Formato JSON:
{
  "date": "YYYY-MM-DD",
  "occupancy": {
    "market": {"rate_pct": X, "trend": "up|flat|down", "source": "report name"}
  },
  "construction_mw": {
    "market": {"mw_building": X, "delivery_date": "Q-YYYY", "delayed": true|false}
  },
  "colocation_pricing": {
    "market": {"usd_kw_month": X, "trend": "up|flat|down", "hd_premium_pct": X}
  },
  "lead_times": {
    "transformers_months": X,
    "switchgear_months": X,
    "generators_months": X,
    "liquid_cooling_months": X,
    "trend": "lengthening|stable|shortening"
  },
  "interconnection_queue": {
    "pjm_gw_pending": X,
    "avg_approval_months": X,
    "ferc_changes": "descripción o null"
  },
  "thesis_impact": "Resumen de 2-3 frases: ¿la infraestructura física sigue siendo cuello de botella?"
}
```

---

## Prompt 2: Superciclo de Materias Primas

```
Fecha: {FECHA}

Actualiza el estado del superciclo de materias primas críticas para infraestructura de IA:

1. COBRE:
   - Precio spot LME ($/ton) y variación mensual
   - Inventarios LME (tons) y tendencia
   - ¿Disrupciones mineras este mes? (Grasberg, Kamoa-Kakula, Chile)
   - Demanda de data centers estimada vs demanda EV vs demanda tradicional
   - Precio del ETF COPX y variación mensual

2. URANIO:
   - Precio spot U3O8 ($/lb) — Numerco, UxC, TradeTech
   - Variación mensual
   - Inventarios globales estimados
   - ¿Producción de Kazatomprom normalizada o en disrupción?
   - Contratos a largo plazo firmados este mes
   - Precio de URA, URNM, U.UN y variación mensual

3. GAS NATURAL:
   - Henry Hub ($/MMBtu) y variación mensual
   - ¿Demanda de plantas de generación para data centers está impactando precios?
   - Producción de EQT y guidance

4. TIERRAS RARAS / LITIO:
   - Precio de litio (carbonato, $/ton)
   - ¿Cambios en política de exportación china?
   - Estado de MP Materials (Mountain Pass)

Formato JSON:
{
  "date": "YYYY-MM-DD",
  "copper": {
    "lme_spot": X, "change_1m": "X%", "inventories_tons": X, "inv_trend": "up|down",
    "disruptions": "descripción o null", "copx_price": X, "copx_change_1m": "X%"
  },
  "uranium": {
    "spot_lb": X, "change_1m": "X%", "inventories": "low|normal|high",
    "kazatomprom_status": "normal|disrupted",
    "ltc_signed_this_month": X, "ura_price": X, "urnm_price": X, "u_un_price": X
  },
  "natgas": {
    "henry_hub": X, "change_1m": "X%", "dc_demand_impact": "visible|minimal"
  },
  "rare_earths": {
    "lithium_carbonate_ton": X, "change_1m": "X%",
    "china_export_policy": "unchanged|restrictive|easing"
  },
  "supercycle_status": "accelerating|stable|decelerating",
  "thesis_note": "2 frases"
}
```
