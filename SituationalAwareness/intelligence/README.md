# Intelligence Engine — Situational Awareness LP Thesis Monitor

**Fecha:** 2 de abril de 2026
**Objetivo:** Monitorizar señales que validen o invaliden la tesis de inversión en infraestructura física de IA
**Método:** Prompts a LLMs con acceso a web/finance (Gemini, Perplexity, Claude + web search)
**Coste:** $0 en APIs de terceros. Solo herramientas gratuitas o ya disponibles.

---

## Arquitectura

```
Frecuencia → Prompt → LLM con web access → JSON estructurado → Dashboard HTML
```

## Archivos de prompts

| Archivo | Frecuencia | Datos |
|---------|-----------|-------|
| [daily.md](daily.md) | Diario | Precios, commodities, futuros, noticias, SEC filings |
| [weekly.md](weekly.md) | Semanal | Hashrate BTC, short interest, ETF flows, insider trading |
| [monthly.md](monthly.md) | Mensual | Ocupación DC, lead times, permisos interconexión |
| [quarterly.md](quarterly.md) | Trimestral | 13F SA LP, earnings hiperscalers, capex guidance |
| [adhoc.md](adhoc.md) | Ad-hoc | Regulación nuclear, export controls, geopolítica, PPAs |

## Herramientas recomendadas por prompt

| Herramienta | Para qué | Gratis |
|-------------|----------|--------|
| Gemini + Google Finance | Precios, cotizaciones, futuros, commodities | Sí |
| Perplexity | Noticias, earnings, SEC filings, research | Sí (con límite) |
| Claude + WebSearch | Análisis profundo, síntesis de múltiples fuentes | Sí (en Claude Code) |
| Google News RSS | Alertas de noticias por keyword | Sí |
| SEC EDGAR RSS | Filings nuevos de SA LP (CIK 0002045724) | Sí |
