# Ad-Hoc Intelligence Prompt

**Frecuencia:** Cuando hay un evento relevante (breaking news, regulación, geopolítica)
**Herramienta recomendada:** Claude + WebSearch (análisis profundo) o Perplexity (speed)
**Trigger:** Alertas de Google News, RSS de SEC EDGAR, o mención en daily scan

---

## Prompt 1: Evento Regulatorio Nuclear

```
EVENTO: {DESCRIPCIÓN DEL EVENTO}
Fecha: {FECHA}

Analiza el impacto de este evento regulatorio nuclear sobre la tesis de inversión:

CONTEXTO: La tesis anticipa que clusters de IA de 1-10 GW necesitarán energía nuclear
descentralizada (SMR). Las empresas clave son: Oklo (OKLO), NuScale (SMR),
Constellation Energy (CEG), Cameco (CCJ), Rolls-Royce SMR (RR.L).

ANALIZAR:
1. ¿Qué cambió exactamente? (nueva certificación, rechazo, retraso, nueva regulación)
2. ¿A qué empresa(s) afecta directamente?
3. ¿Acelera o retrasa el timeline de despliegue de SMR?
4. ¿Cambia el competitive landscape entre Oklo, NuScale y Rolls-Royce?
5. ¿Impacto en precio de uranio?
6. ¿Hay reacción del mercado ya?

Formato JSON:
{
  "event": "descripción",
  "date": "YYYY-MM-DD",
  "impact_assessment": {
    "tickers_affected": {"TICKER": "bullish|bearish|neutral"},
    "smr_timeline": "accelerated|unchanged|delayed",
    "uranium_impact": "bullish|bearish|neutral",
    "thesis_impact": "strengthening|neutral|weakening"
  },
  "action_required": "none|monitor|re-evaluate|trade",
  "reasoning": "3-5 frases"
}
```

---

## Prompt 2: Export Controls / Sanciones

```
EVENTO: {DESCRIPCIÓN}
Fecha: {FECHA}

Analiza nuevas sanciones o export controls sobre semiconductores/tecnología:

CONTEXTO: La tesis de SA LP asume que EE.UU. necesita soberanía computacional.
Export controls afectan a: TSMC, ASML, SMIC, SK Hynix, Samsung.
SA LP vendió TSMC/ASML por riesgo geopolítico. Mantiene Intel (fabricación US) y
Tower Semiconductor (Israel, aliado US).

ANALIZAR:
1. ¿Qué se restringe? ¿A quién? ¿Desde cuándo?
2. ¿Afecta a ASML (litografía)? ¿A TSMC (fabricación)?
3. ¿Beneficia a Intel Foundry o Tower Semiconductor? (reshoring)
4. ¿Impacto en cadena de suministro de GPUs NVIDIA?
5. ¿China puede sustituir con SMIC o Huawei Ascend?
6. ¿Impacto en ETFs: SMH, EWT, KCHIP, CQQQ?

Formato JSON:
{
  "event": "descripción",
  "date": "YYYY-MM-DD",
  "restrictions": {"what": "X", "who": "X", "when": "X"},
  "impact": {
    "losers": [{"ticker": "X", "reason": "X"}],
    "winners": [{"ticker": "X", "reason": "X"}],
    "reshoring_benefit": true|false,
    "gpu_supply_impact": "constrained|unchanged|eased"
  },
  "thesis_impact": "strengthening|neutral|weakening",
  "action_required": "none|monitor|re-evaluate",
  "reasoning": "3-5 frases"
}
```

---

## Prompt 3: Tensión Geopolítica Taiwán-China

```
EVENTO: {DESCRIPCIÓN}
Fecha: {FECHA}

Evalúa escalada de tensión entre China y Taiwán:

CONTEXTO: Taiwán = TSMC (49% producción mundial chips avanzados), Hon Hai (servidores),
Quanta Computer. SA LP vendió TSMC por este riesgo exacto. Si hay conflicto militar,
la cadena de semiconductores global colapsa. Intel y Tower Semi se revalorizan.

ANALIZAR:
1. ¿Qué pasó exactamente? (ejercicio militar, declaración, bloqueo, sanción)
2. Severidad: 1-10 (1=retórica, 10=acción militar)
3. ¿Impacto en cadena de suministro de chips si escala?
4. ¿Beneficiarios si se confirma desacoplamiento? (INTC, TSEM, ASML, reshoring)
5. ¿Impacto en ETFs asiáticos (EWT, AAXJ, KCHIP)?
6. ¿Historicamente, cuánto duran estos episodios y cómo se resuelven?

Formato JSON:
{
  "event": "descripción",
  "date": "YYYY-MM-DD",
  "severity": X, // 1-10
  "supply_chain_risk": "low|medium|high|critical",
  "tickers_at_risk": [{"ticker": "X", "exposure": "X%_revenue_taiwan"}],
  "tickers_beneficiaries": [{"ticker": "X", "reason": "reshoring"}],
  "historical_parallel": "descripción de evento similar pasado y resolución",
  "thesis_impact": "SA LP thesis of US sovereignty VALIDATED if tension rises",
  "action_required": "none|hedge|reduce_asia|increase_us",
  "reasoning": "3-5 frases"
}
```

---

## Prompt 4: Nuevo PPA Nuclear/Renovable con Hiperscaler

```
EVENTO: {DESCRIPCIÓN — ej: "Google firma PPA de 2GW con Constellation Energy"}
Fecha: {FECHA}

Analiza un nuevo contrato PPA (Power Purchase Agreement) de un hiperscaler:

CONTEXTO: Los PPAs son la señal MÁS DIRECTA de demanda real de energía para IA.
Cada GW contratado valida la tesis de "power crunch". SA LP apuesta a que la demanda
supera la oferta de energía disponible.

ANALIZAR:
1. ¿Quién firma? (hiperscaler + utility/generador)
2. ¿Cuántos MW/GW? ¿Por cuántos años?
3. ¿Qué tipo de energía? (nuclear, solar, eólica, gas, fuel cells)
4. ¿Precio estimado del PPA ($/MWh)?
5. ¿Impacto en empresas de la cartera? (BE, CEG, NEE, IBE)
6. ¿Acumula presión sobre la red pública? (menos MW disponibles para otros)

Formato JSON:
{
  "event": "descripción",
  "date": "YYYY-MM-DD",
  "ppa_details": {
    "buyer": "hiperscaler",
    "seller": "utility/generator",
    "capacity_mw": X,
    "duration_years": X,
    "energy_type": "nuclear|solar|wind|gas|fuel_cell",
    "price_mwh": X
  },
  "market_impact": {
    "grid_pressure": "increasing|stable",
    "beneficiaries": [{"ticker": "X", "reason": "X"}],
    "validates_thesis": true|false
  },
  "cumulative_gw_contracted_ytd": X,
  "thesis_note": "2 frases"
}
```

---

## Prompt 5: Filing 13D/A de SA LP sobre CORZ (Activista)

```
EVENTO: Nuevo filing 13D/A de Situational Awareness LP sobre Core Scientific (CORZ)
Fecha: {FECHA}

Busca el filing en SEC EDGAR y analiza:

1. ¿Cuántas acciones tiene ahora? (vs anterior: 28.756.478)
2. ¿Qué % del float/outstanding representa?
3. ¿Incrementó o redujo?
4. ¿Hay algún "purpose of transaction" nuevo? (cambio de board, propuesta, etc.)
5. ¿Hay algún acuerdo o carta adjunta?
6. ¿Compró a mercado o vía transacción privada?

Formato JSON:
{
  "filing_date": "YYYY-MM-DD",
  "shares_current": X,
  "shares_previous": X,
  "change_shares": X,
  "pct_ownership": X,
  "direction": "UP|DOWN|FLAT",
  "purpose": "descripción del purpose of transaction",
  "new_agreements": "descripción o null",
  "thesis_signal": "Si incrementa = más convicción en reconversión. Si reduce = posible salida.",
  "action": "monitor|alert"
}
```
