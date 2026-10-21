# ARKAIOS–EML Lab · etapa B (v2): multiplicación K=571 y división K=2,987

Continúa el paquete `README.md` (prioridad **B**: expresiones más cortas). Todo sigue siendo **aritmética real**
con hojas `1, x, y` y la misma métrica K (símbolos del árbol en RPN, Tabla 4 de Odrzywołek).

## 1. Resultado

| expresión | K árbol | prof. | nodos E únicos | dígitos para (3,3) | antes |
|---|---:|---:|---:|---:|---|
| **M571** = x·y | **571** | 24 | 59 | 540 | M_opt K=631 |
| **V2987** = x/y (y≠0) | **2,987** | 36 | 125 | **540** (0.1 s) | V_opt K=88,715, 7,740 dígitos (31 s) |

Reducción de la división: **88,715 → 2,987 (−96.6 %)**, y además mucho mejor condicionada numéricamente.
Archivos: `expressions/M571.rpn`, `expressions/V2987.rpn`, `expressions/manifest_v2.json` (SHA-256:
`05be458b…9caa`, `e6ae49f1…08c5`).

## 2. Construcción

**M571.** Misma fórmula que M_opt, `x·y = (Px−Qx)(Py−Qy) = A − B`, solo cambia el orden de argumentos dentro de
`Add19(a,b)` (en Add19 el argumento `a` aparece 3 veces y `b` una): se enumeraron las 2⁶ ordenaciones y se tomó la más corta.

**V2987.** En vez de `M(M(x,y), 1/y²)` (que mete una multiplicación completa dentro de otra), el factor 1/y² se
**pliega en los exponentes**:

```
x/y = x·y / y² = (A − B)/q = (1+A)/q − (1+B)/q,      q = M571(y,y) = y²
T/q = exp( ln T − ln q ) = exp( E(ln ln T, q) )        válido si T > 1 y q > 0
V2987 = Sub19( divq(1+A, q), divq(1+B, q) ),   divq(T,q) = P(E(L(L(T)), q)),   1+T = Add19(1, T)
```

**Dominio (argumento completo, todo real):** `A = PxPy + QxQy > 0` y `B = PxQy + QxPy > 0` (sumas de exponenciales),
así que `1+A > 1` y `1+B > 1`; por tanto `L(T) = ln T > 0` y `L(L(T))` es real; `q = y² > 0` para y≠0;
`Sub19`, `Add19`, `P`, `Q`, `L(Q(·))` son los bloques ya verificados como globales. Para y = 0 la expresión falla
en el dominio (correcto: división por cero).

El desplazamiento +1 es necesario: sin él, `A/q − (1+B)/q = x/y − 1/q` (la verificación lo detectó: error 0.25 en (1,2)).

## 3. Verificación (`results/09_division_v2.txt`, `results/10_*.txt`)

| prueba | alcance | resultado |
|---|---|---|
| M571, precisión adaptativa + chequeo de dominio | 81 pares en [−3,3]² | 0 fallos, error rel. máx 8.5e−120 |
| V2987, ídem | 72 pares (x∈[−3,3], y∈±{0.5,1,2,3}) | 0 fallos, error rel. máx 1.2e−119, ≤540 dígitos |
| V2987, puntos extra | (0.5,0.25), (1.5,0.1), (−2.75,0.125), (−2,4), (4,4), (3.5,−2.25), (−0.001,2) | 0 fallos, ≤3,900 dígitos |
| verificador independiente (pila pura, sin DAG) | V2987: 6 puntos; M571: 5 puntos, 650 dígitos | todos OK |
| y = 0 | — | rechazado con DomainError |
| `tests/` | 7 pruebas | OK |

Comparación directa con V_opt en los mismos puntos (máx. 30,000 dígitos): V_opt **no termina** en (0.5,0.25),
(1.5,0.1) ni (4,4); V2987 sí (149, 540 y 3,900 dígitos).

## 4. Cambio en el evaluador (transparencia)

Se añadió `adaptive_eval2` / `eval_mp_capped` en `evaluators.py`: si un **argumento de exp** supera 10^(dps−10)
se aborta y se reintenta con el doble de dígitos. Motivo: con pocos dígitos, una cancelación produce basura
(p. ej. un 10^50 espurio) y `exp(exp(10^50))` cuelga mpmath. Sigue siendo **heurístico**, no aritmética de intervalos.
El evaluador original no se modificó.

## 5. Resultado negativo útil: V2959

Con la descomposición `t = F − G`, `F = e^{e^t}`, `G = e^{e^t} − t` (ambas > 1, mín. G ≈ 2.33) se obtiene una división
aún más corta, **K=2,959**, correcta en los reales, pero numéricamente patológica: (2,2) ya necesita 7,740 dígitos y
(3,3) requiere argumentos de exp de ~10^(4.6·10⁹) (inviable). Se descarta: **más corta ≠ evaluable**.

## 6. Límites (qué NO está demostrado)

* Optimalidad de 571 / 2,987; ninguna cota inferior.
* Rango práctico: `|y| ≲ 0.01` o `|y| ≳ 6` necesita > 30,000 dígitos (el costo de `Sub19(a,b)` crece como e^{|b|} y el de
  M(t,t) como ~10^(c·e^{2|t|})). Es propiedad de los bloques, no un fallo de dominio, pero limita el uso real.
* Lo de `README.md` §10 sigue vigente (universalidad, rigor de la precisión adaptativa, otras plataformas).

## 7. Siguiente paso sugerido

En V2987, `q` (571 símbolos) aparece **4 veces** (≈2,284 de 2,987). Una división más corta pasa por: (i) un cuadrado
`y²` o un `ln|y|` dedicado más corto que 571; (ii) una resta con el argumento pesado en la posición que aparece una sola vez;
(iii) extender el buscador de §6 con bloques P, Q, L(Q(·)), divq como hojas de costo ponderado.
