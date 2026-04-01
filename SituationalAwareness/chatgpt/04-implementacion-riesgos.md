# Implementación y Riesgos

---

## Estructura en capas

La implementación "global" de esta tesis funciona mejor en capas:

### Capa 1 — Exposición base amplia (ETFs grandes)
- CNDX.L, SMH.L, INTL.L
- Liquidez alta, diversificación, beta IA generalizado

### Capa 2 — Satélites en nodos físicos (centros de datos + electrificación)
- EQIX, ETN
- Drivers parcialmente distintos al software (demanda eléctrica, espacio físico)
- Descorrelación parcial con correcciones "growth"

### Capa 3 — Satélite especulativo (mineros/hosting) — Solo si se tolera volatilidad
- CORZ
- Alto riesgo, alta convexidad
- La propia cartera 13F sugiere que SA LP usa derivados para modular esta exposición

---

## Riesgo de concentración por factor

**Riesgo dominante en acciones/ETFs:** muchos nombres de la cadena de IA tienden a moverse juntos en:
- Shocks de tipos de interés
- Correcciones "growth"
- Cambios de expectativas de capex de los hiperscalers

**Mitigación:** la cartera no debe ser "todo semis" o "todo cloud" sino incluir **nodos con drivers parcialmente distintos** (electrificación vs software, colocation vs chips).

---

## Riesgos de derivados (CALL)

Las opciones CALL pueden replicar la convexidad que se observa en el 13F, pero añaden:

| Riesgo | Descripción |
|--------|-------------|
| **Pérdida máxima de prima** | Si la acción no sube lo suficiente, pierdes el 100% de la prima pagada |
| **Decay temporal (theta)** | Las opciones pierden valor cada día que pasa |
| **Sensibilidad a volatilidad implícita (vega)** | Un crash de vol puede destruir el valor incluso si la acción no baja |
| **Riesgo de "roll"** | Si la tesis necesita más tiempo del esperado, hay que renovar opciones (coste adicional) |

El hecho de que el 13F muestre líneas CALL refuerza que **parte de la exposición buscada no es lineal** — es una apuesta de convexidad, no de carry.

---

## Riesgo de liquidez/tamaño

| Instrumento | MCap | Riesgo |
|-------------|------|--------|
| CNDX.L | ~21,3 B$ | Bajo — alta liquidez |
| ETN | ~136,6 B$ | Bajo — muy líquido |
| EQIX | ~95,5 B$ | Bajo |
| SMH.L | ~4,6 B$ | Medio |
| CORZ | ~4,7 B$ | Medio-alto — spreads potencialmente amplios |
| INTL.L | ~766,8 M$ | Alto — menor liquidez |
| **KLWD.L** | **~232,2 M$** | **Muy alto — spreads amplios, riesgo de ejecución, sensibilidad a flujos** |

**KLWD.L es el eslabón más débil en liquidez.** Su capitalización es ~90x menor que CNDX.L, lo que implica spreads más amplios y mayor riesgo de ejecución.
