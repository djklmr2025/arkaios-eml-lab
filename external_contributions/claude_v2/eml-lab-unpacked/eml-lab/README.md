# ARKAIOS–EML Lab · paquete reproducible (borrador para revisión cruzada)

Operador: **eml(a,b) = exp(a) − ln(b)**, hojas permitidas: `1`, `x`, `y`. Todo aquí es **aritmética real**: en cada
construcción, todo argumento de ln es > 0 para cualquier real de entrada (se prueba abajo y se verifica numéricamente).

> **Estado:** resultados *no definitivos* hasta pasar la revisión cruzada (ChatGPT, Copilot, Antigravity).
> Nada de lo de aquí demuestra universalidad de EML (π, i, trigonométricas): solo aritmética real (+, −, ×, ÷).

## 1. Contenido

| ruta | qué es |
|---|---|
| `eml_lab/core.py` | DAG con hash-consing + medidas (K, hojas, profundidad, nodos únicos), RPN |
| `eml_lab/constructions.py` | todas las construcciones: original, intermedia (ln del artículo) y optimizada |
| `eml_lab/evaluators.py` | evaluadores: `tree` / `dag` / `dag_stable`, float64 y mpmath (con **chequeo de dominio**), precisión adaptativa |
| `eml_lab/search.py` | enumerador exhaustivo de expresiones reales (con sus límites, ver §6) |
| `scripts/01…07` | conteos, exportación, verificación mpmath, benchmarks float64, métricas de ejecución, buscador, validación de documentos externos |
| `tools/independent_check.py` | verificador **independiente** (máquina de pila, sin compartir código) para cruzar resultados |
| `expressions/` | expresiones **completas** (`*.rpn`), grafos (`*.dag.json`) y `manifest.json` con SHA-256, K, profundidad |
| `results/` | salidas de referencia de cada script (las de esta ejecución) |
| `original_scripts/`, `original_results/` | scripts de las sesiones previas **sin modificar** y sus logs (`README_ORIGINALS.md`) |
| `AUDIT_EXTERNAL_CLAIMS.md` | revisión del informe de Antigravity y del resumen de Copilot |

## 2. Ejecución

```bash
pip install -r requirements.txt      # numpy, mpmath
python -m unittest discover -s tests # <1 s
./run_all.sh                         # todo (~10 min; 03c ~3 min por y=3)
python tools/independent_check.py expressions/M_opt.rpn mul --dps 450 --points "3,3;-2,0.5;0,1"
```
Python ≥ 3.10. Sin GPU, sin red.

## 3. Métricas (se reportan por separado a propósito)

* **K** = símbolos del **árbol** en RPN = 2·hojas − 1 (misma métrica que la Tabla 4 de Odrzywołek). *No* es el tamaño del DAG.
* **nodos E únicos** = tamaño del DAG (compresión del grafo).
* **llamadas exp/ln** = costo de ejecución, depende de la estrategia: `tree` (todo recomputado), `dag` (memoizado), `dag_stable` (+ reescritura exacta `eml(a, exp(w)) = exp(a) − w`, válida en todos los reales, no cambia el dominio).
* **precisión/estabilidad** = tercera dimensión, independiente de las dos anteriores.

## 4. Expresiones y resultados esperados (`results/01_counts.txt`)

| expresión | K árbol | hojas | prof. | nodos E únicos |
|---|---:|---:|---:|---:|
| Sub original | 31 | 16 | 7 | 12 |
| Add original | 139 | 70 | 13 | 21 |
| M original | 14,471 | 7,236 | 37 | 107 |
| V original | 21,478,743 | 10,739,372 | 82 | 284 |
| **Sub19** (`11yy1EEE1EEyx1EE1EE` = x−y) | 19 | 10 | 6 | 9 |
| **Add19** (`x11xx1EEE1EEy1EE1EE` = x+y) | 19 | 10 | 8 | 9 |
| **M_opt** | 631 | 316 | 24 | 59 |
| **V_opt** = M(M(x,y), 1/y²) | 88,715 | 44,358 | 58 | 180 |

Construcción (todas reales): `P(t)=exp(t)`, `Q(t)=exp(t)−t ≥ 1`, `Z=0`, `ln u = E(1,E(E(1,u),1))` (u>0),
`R_y(t)=exp(y)−t`, `Sub(x,y)=E(ln R_y(y), P(R_y(x)))` (el primer argumento de ln es `e^y−y ≥ 1`),
`x = P(x) − Q(x)` (ambos positivos), `x·y = (Px−Qx)(Py−Qy) = [PxPy+QxQy] − [PxQy+QxPy]` con `Pu·Pv = P(u+v)`, `Pu·Qv = P(u + ln Qv)`, `Qu·Qv = P(ln Qu + ln Qv)`,
`1/y² = exp(0 − ln(y·y))`, `x/y = M(M(x,y), 1/y²)` (y≠0). Expresiones completas: `expressions/*.rpn`.
El orden de argumentos importa: `M(M(x,y),r)`=88,715 frente a 133,051–7,000,831 en otras ordenaciones.

## 5. Verificación (resultados de referencia)

| prueba | alcance | resultado |
|---|---|---|
| Sub/Add (orig., paper-ln, K=19), mpmath 400 díg. | 196 pares en [−30,30]² | 0 fallos de dominio, error máx 5.6e−388 |
| M (orig., paper-ln, opt), precisión adaptativa | 81 pares en [−3,3]² | 0 fallos de dominio, error máx 3.9e−119 (≤418 díg.) |
| **V_opt (prioridad A)**, precisión adaptativa | 42 pares (x∈{−2…2}, y∈{±0.5,±1,±2}) + 9 pares con y=3 (`03c`) + 21 de la corrida completa (`03b`) = **72/72 pares** | 0 fallos de dominio reales; error máx ≈1.5e−116; V(3,3) necesitó 7,589 dígitos (174 s) |
| verificador independiente (pila, sin DAG, sin reescritura) | M: 4 puntos; V: 3 puntos | todos OK |
| `tests/` | 6 pruebas | OK |

Nota de transparencia: la primera corrida completa de V (`results/03b_...`) marcó 9 "fallos de dominio" en y=3. Eran un **artefacto**:
con 60 dígitos de partida, `M(3,3)` produce un 0 espurio dentro del árbol y el chequeo de dominio lo rechazaba. Se corrigió el evaluador adaptativo
(reintenta con más dígitos y solo reporta fallo si persiste) y esos 9 pares se re-verificaron (`results/03c_verify_V_y3.txt`).

## 6. Buscador y límites de exhaustividad

`scripts/06_search.py`: enumera árboles con hojas {1,x,y}, conservando solo funciones **reales** (todo ln con argumento >0 en los 8 puntos de prueba, finitas y <1e250), deduplicadas por vector de valores (se guarda la primera = la más corta).

* **Exhaustivo** hasta 12 hojas (K=23) en la corrida de referencia (hasta 13 en las originales). Resultados verificados en mpmath: `0`→K7, `−1`→K17, `2`→K19, `x−y`→K19, `x+y`→K19, `−x`→K17, `2x`→K19 (coinciden con los valores "sin reales extendidos" entre paréntesis de la Tabla 4: −1→17, 2→19).
* **No encontrados** con ≤12 hojas: `x·y`, `x/y`, `1/x`, `x²`, `x/2`. El *meet-in-the-middle* (particiones balanceadas) hasta 24 hojas tampoco: **no es exhaustivo** por encima de nmax+1 hojas. Conclusión permitida: una multiplicación real, si es más corta que 631, tiene K > 23 (exhaustivo) y no aparece en particiones balanceadas hasta K=47.
* **Límites**: (i) equivalencia comprobada solo en 8 puntos (no es prueba; todo candidato se verifica en rejilla de 169 puntos con 400 dígitos); (ii) el filtro de finitud en float64 puede descartar fórmulas válidas con exponenciales enormes; (iii) con puntos de prueba estrechos (`--points narrow`) aparecen falsas fórmulas "globales" (p. ej. `x+y`, `−x` con 52 de 169 puntos fuera del dominio real): ver `results/06_search_narrow.txt`.

## 7. Casos de fallo numérico (`results/04_float64_bench.txt`, `results/failures_M.csv`)

float64, rejilla [−8,8]² paso 0.25: Sub19/Add19 `dag` 3835/4225 → `dag_stable` 4225/4225; **M_opt** 1230 → 1615 de 4225; **V_opt** 96 → 404 de 4160.

**M(3,3)** (la diagonal): el árbol puro tiene exp-argumentos de ~10^298; el resultado frente a los dígitos de trabajo es

| dígitos | 50 | 100–290 | 300 | ≥320 |
|---|---|---|---|---|
| M(3,3) | 1.3e−51 | 0.0 | 9.55 | **9.0** |

La causa **no es ln(0)** ni la diagonal: todos los ln del árbol son positivos (verificado en 400 dígitos); es cancelación catastrófica tras exponenciales anidadas. En float64: `M(1,1)=−inf`, `M(2,2)=nan`, `M(3,3)=nan` (0.0 con reescritura estable). La reescritura quita desbordes, **no** la cancelación.

Observación incómoda pero útil: M más corta ≠ más precisa. En (0.5,0.5), `M_orig` da 0.25 exacto y `M_opt` 0.2499999999999929.

## 8. Ejecución comparada (prioridad D, `results/05_execution_metrics.txt`)

| expresión | estrategia | K | nodos E únicos | exp | ln |
|---|---|---:|---:|---:|---:|
| M_opt | tree | 631 | 59 | 315 | 315 |
| M_opt | dag | 631 | 59 | 59 | 59 |
| M_opt | dag_stable | 631 | 59 | 36 | 10 |
| V_opt | tree | 88,715 | 180 | 44,357 | 44,357 |
| V_opt | dag | 88,715 | 180 | 180 | 180 |
| V_opt | dag_stable | 88,715 | 180 | 111 | 32 |

El resultado numérico se reporta aparte: no es evidencia de mejor respuesta que una estrategia sea más barata.

## 9. Estado de las prioridades

* **A** hecha (ver §5), con la advertencia de los 7,589 dígitos para y=3.
* **B** *no* lograda más allá de la búsqueda exhaustiva de §6. Pendiente: búsqueda sobre árboles con bloques P, Q, L(Q(·)) como hojas con costo ponderado; cota inferior.
* **C** prototipo: `adaptive_eval` (heurística: dígitos ≈ log10 del mayor exp-argumento + objetivo + guarda, confirmada con +60 dígitos). **No es riguroso** (no es aritmética de intervalos).
* **D** hecha (§8).

## 10. Qué NO está demostrado

Universalidad (π, i, trig); optimalidad de K=631 / 88,715; cota inferior de cualquier multiplicación real; corrección de las fórmulas fuera de los reales con rama principal; rigor de la precisión adaptativa; resultados de float64 en otras plataformas (los de aquí: CPython + NumPy).
