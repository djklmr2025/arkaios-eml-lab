# ARKAIOS–EML Lab · v3: límites teóricos de EML real y experimento con la rama compleja

Continúa `README.md` (§10, "universalidad no demostrada") y `README_v2.md`. Dos partes: un **argumento teórico**
(qué es imposible en la clase real) y un **experimento numérico** (cómo la rama principal del logaritmo complejo
abre la puerta a i, π, e^{ix}, cos y sin, y qué precio se paga).

---

## 1. Límites teóricos de EML real

**Clase real.** Árboles con hojas `1, x, y` y nodos `eml(a,b) = exp(a) − ln(b)`, evaluados en ℝ. El dominio D_f es el conjunto
de puntos donde todo argumento de ln es > 0.

**Proposición 1 (definibilidad).** Para toda expresión EML real f, tanto D_f como la función f : D_f → ℝ son definibles en la
estructura ℝ_exp = (ℝ, +, ·, <, exp).
*Prueba (inducción sobre el árbol).* Las hojas son definibles. Si a y b lo son, el dominio de eml(a,b) es
D_a ∩ D_b ∩ {b > 0}, que es definible. Además ln es definible (`ln b = t  ⇔  exp(t) = b`), y la resta también lo es. □

**Teorema (Wilkie, 1996).** ℝ_exp es **o-minimal**: todo subconjunto de ℝ definible es una unión finita de puntos e intervalos.

**Corolarios para EML real.**

1. **Sin oscilación global.** El conjunto de ceros de f es definible, así que tiene finitas componentes. Por eso ninguna
   expresión EML real coincide con sin x, cos x ni con ninguna función con infinitos ceros aislados en una semirrecta
   (por ejemplo [0, ∞)). Una búsqueda de sin/cos en la clase real **está condenada a fallar**, por grande que sea K.
2. **Monotonía por trozos.** Por el teorema de monotonía o-minimal, cada f es, a trozos finitos, continua y estrictamente
   monótona o constante. En particular, f es monótona cerca de +∞ y no existe una f periódica no constante.
3. **Ni siquiera localmente.** Bianconi (1997) probó que la restricción de sin a cualquier intervalo abierto **no** es
   definible en ℝ_exp. Si eso es correcto, ninguna expresión EML real es igual a sin x ni en un intervalo pequeño.
   Aproximarla es posible; igualarla, no.
4. **La unidad imaginaria.** i ∉ ℝ, así que trivialmente queda fuera de la clase real.
5. **π como constante: abierto.** No se sabe si π es un valor de alguna expresión EML real sin variables. Se cree que no
   (la pregunta está ligada a la conjetura de Schanuel), pero no está demostrado. Este apartado **no** afirma imposibilidad.

**Conclusión.** La "universalidad" (calculadora científica completa) es **imposible** en la clase real. Esto se
demuestra, no solo se observa. Para alcanzar la trigonometría hay que salir a ℂ, tal como hace el artículo de Odrzywołek.
La fórmula de Euler e^{ix} = cos x + i sin x no es un adorno: es el único camino.

> **Referencias a confirmar antes de citar:**
> A. J. Wilkie, *J. Amer. Math. Soc.* 9 (1996) 1051–1094.
> R. Bianconi, *J. Symbolic Logic* 62 (1997), resultado de no definibilidad del seno restringido en ℝ_exp.
> L. van den Dries, *Tame Topology and O-minimal Structures* (1998), para el teorema de monotonía.

---

## 2. Experimento: rama principal del logaritmo complejo (`scripts/11_complex_branch.py`)

Es el mismo DAG con otra aritmética: `eml(a,b) = exp(a) − Log(b)` en ℂ, con Log de rama principal (arg ∈ (−π, π]) y
mpmath. Evaluador en `eml_lab/complex_eval.py`; construcciones en `eml_lab/complex_constructions.py`.

### 2.1 Los bloques reales se rompen en ℂ

Con 2000 puntos complejos aleatorios en [−3,3] + [−3,3]i, la fracción de resultados correctos es:

| bloque | correcto |
|---|---:|
| Sub19 (x−y) | 1465/2000 (73 %) |
| Add19 (x+y) | 1417/2000 (71 %) |
| Neg (−x) | 1577/2000 (79 %) |
| L (ln x) | 2000/2000 |

La causa es que `Log(exp(w)) = w` solo se cumple si Im w ∈ (−π, π]. Cada vez que una parte imaginaria intermedia sale de esa
franja, el resultado se desplaza en 2πi.

### 2.2 Estrategia que sí funciona

Hay dos reglas:

- **Nunca sumar o restar números con parte imaginaria grande.** La rotación va **dentro** de exp.
- **El producto se hace con logaritmos:** `u·v = exp(Log u + Log v)`. La ambigüedad de 2πi del Log desaparece al aplicar exp.

Construcciones:

```
W   = eml(0, −1) = 1 − Log(−1) = 1 − iπ          (−1 es real exacto: Log(−1) = iπ está bien definido)
W/2 = exp(Log W − ln 2)                          (W está lejos del corte)
iπ/2 = 1/2 − W/2,     −iπ/2 = W/2 − 1/2,     i = exp(iπ/2)
π   = (iπ)·(−i)                                  (¡una constante REAL obtenida pasando por ℂ!)
e^{ix} = e^{i·Px} · e^{−i·Qx},   con i·Px = exp(iπ/2 + x),  i·Qx = exp(iπ/2 + ln Qx)   (x = Px − Qx)
cos x = (2cos x + 3)/2 − 3/2,   sin x = cos(x − π/2)
```

### 2.3 Resultados

| objeto | K árbol | nodos E únicos | correcto | estable (7 precisiones o +37 díg.) |
|---|---:|---:|---|---|
| 1 − iπ | 25 | — | sí | 7/7 |
| i | 485 | — | sí | 7/7 |
| iπ | 1,947 | — | sí | 7/7 |
| π/2 | 1,927 | — | sí | 7/7 |
| **π** | **6,319** | — | sí | 7/7 |
| e^{ix} | 5,783 | 91 | 646/646 pts en [−40,40] | 646/646 |
| **cos x** | **23,719** | 168 | 646/646 | 646/646 |
| **sin x** | **139,639** | 193 | 646/646 | 646/646 |

El error máximo es ≈ 3e−64 con 60 o más dígitos. Los 646 puntos incluyen 0, ±1e−12, ±π y π/2.

### 2.4 Tres hallazgos (incluidos dos errores míos, detectados por las pruebas)

1. **Una constante puede caer exactamente sobre el corte.** La primera ruta para iπ, `Sub19(1, 1−iπ)`, evalúa internamente
   Log de un número que vale **exactamente −e**. Su parte imaginaria es puro ruido de redondeo, y el signo de ese ruido decide
   entre +iπ y −iπ. Resultado: correcto con 40, 57, 233 y 300 dígitos, e incorrecto con 73, 101 y 150. Se conserva como
   contraejemplo (`IPI_UNSTABLE`).
   Lección: en ℂ, "algebraicamente correcto" no basta; también importa **dónde** pasan los valores intermedios.
2. **El error invisible.** Con la ruta inestable, e^{ix} salía conjugado en 202 puntos, pero cos x y sin x salían bien. La razón
   es que cambiar i por −i deja intactos cos y sin (son simétricos bajo conjugación). Solo la prueba directa de e^{ix} lo detectó.
3. **Huecos de dominio.** La primera versión de sin fallaba en x = 0 porque calculaba `Log(0)` en la división por 2.
   Se corrigió desplazando el argumento: `2cos x + 3 ≥ 1` nunca es 0.

**Columna "on_cut" en `results/11`.** Indica que algún argumento de Log está sobre el eje real negativo salvo redondeo.
Para π, π/2 y sin x aparece en posiciones donde ese Log solo entra en `exp(Log u + c)`, así que la ambigüedad se cancela.
La prueba que decide es la de **estabilidad**: el resultado no cambia con más dígitos. Esto es evidencia numérica, **no** una
prueba formal de que la ambigüedad se cancela en todos los casos.

---

## 3. Qué queda demostrado y qué no

| afirmación | estado |
|---|---|
| sin, cos, funciones periódicas: imposibles en EML real | **demostrado** (Prop. 1 + Wilkie); localmente, vía Bianconi (confirmar referencia) |
| π como constante EML real | **abierto** (ligado a Schanuel) |
| i, π, e^{ix}, cos, sin alcanzables con Log principal | **verificado numéricamente** en las construcciones de §2, para x real en [−40, 40] |
| corrección para todo x real | **no demostrado** (hay argumento de diseño, no prueba completa sobre el corte) |
| optimalidad de los K de §2.3 | **no** (son construcciones directas, sin búsqueda) |
| x complejo | **no probado** (los bloques reales fallan en ~25 % de los puntos, §2.1) |

## 4. Conexión con el material de estudio

- *La exponencial compleja* (e^{ix} = cos x + i sin x): §1 explica por qué ese paso es obligatorio, y §2 lo implementa con EML.
- *Círculos infinitos*: la autosemejanza S = π + k²S es el mismo principio que el DAG (calcular una vez lo que se repite).
  Ahora que π es construible vía ℂ, la suma S = π(4+3√2)/8 es un candidato natural para medir su K.
