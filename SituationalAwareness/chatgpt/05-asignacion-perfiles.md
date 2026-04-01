# Asignación por Perfil de Riesgo

**Nota:** Estas asignaciones ilustran estructura por buckets, no una recomendación personalizada. Los porcentajes suman 100% en cada perfil y se basan en repartir "beta IA" (ETFs) y "cuellos físicos" (centros de datos + potencia), dejando el satélite especulativo como opcional.

---

## Perfiles

### Conservador (menos volatilidad, más liquidez)

| Ticker | Nodo | Peso |
|--------|------|------|
| CNDX.L | Hiperscalers + software | **35%** |
| SMH.L | Semiconductores | **25%** |
| ETN | Electrificación/potencia | **20%** |
| EQIX | Centros de datos | **15%** |
| INTL.L | IA temático | **5%** |
| KLWD.L | Cloud software | 0% |
| CORZ | Satélite especulativo | 0% |

**Características:** máxima liquidez, sin exposición especulativa, ~60% en ETFs UCITS.

---

### Equilibrado (diversificación temática + nodos físicos)

| Ticker | Nodo | Peso |
|--------|------|------|
| CNDX.L | Hiperscalers + software | **30%** |
| SMH.L | Semiconductores | **25%** |
| ETN | Electrificación/potencia | **15%** |
| EQIX | Centros de datos | **10%** |
| INTL.L | IA temático | **10%** |
| KLWD.L | Cloud software | **5%** |
| CORZ | Satélite especulativo | **5%** |

**Características:** balance entre beta IA y nodos físicos, exposición controlada al satélite especulativo.

---

### Agresivo (más beta temática y satélite especulativo)

| Ticker | Nodo | Peso |
|--------|------|------|
| SMH.L | Semiconductores | **25%** |
| CNDX.L | Hiperscalers + software | **20%** |
| ETN | Electrificación/potencia | **15%** |
| INTL.L | IA temático | **15%** |
| KLWD.L | Cloud software | **10%** |
| CORZ | Satélite especulativo | **10%** |
| EQIX | Centros de datos | **5%** |

**Características:** máxima exposición temática, mayor volatilidad, 10% en el satélite especulativo (CORZ).

---

## Comparativa visual

```
Conservador:  [===CNDX 35%===][==SMH 25%==][==ETN 20%=][EQIX 15][I5]
Equilibrado:  [==CNDX 30%==][==SMH 25%==][=ETN 15=][EQ10][I10][K5][C5]
Agresivo:     [==SMH 25%==][=CNDX 20%=][=ETN 15=][=INTL 15=][K10][C10][E5]
```

---

## Nota

La propia cartera 13F de SA LP es más agresiva que cualquiera de estos perfiles: usa opciones CALL y tiene concentración >85% en 10 posiciones. Estos perfiles son una **versión diluida y diversificada** de la misma tesis, adaptada para un inversor minorista.
