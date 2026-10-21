# ARKAIOS Relational Core + GLYPH: Limitaciones Técnicas y Fronteras

Este documento establece de forma explícita las fronteras matemáticas, computacionales y semánticas del sistema.

---

## 1. Restricciones de Dominio en el Operador EML

El operador base:
$$E(a, b) = e^a - \ln(b)$$
presenta restricciones asimétricas estrictas:
1. **Argumento Derecho:** $b > 0$. Para cualquier $b \le 0$, el logaritmo natural $\ln(b)$ no está definido en el cuerpo real $\mathbb{R}$.
2. **Dependencia de Aritmética Extendida IEEE 754:**
   - La negación clásica de Odrzywołek $\text{Neg}(z) = \text{Sub}(0, z) = E(\ln(0), e^z)$ evalúa $\ln(0) = -\infty$ y $e^{-\infty} = 0$.
   - En evaluadores numéricos estrictos que arrojan excepciones en $\ln(0)$ (como `math.log(0)` en Python), la evaluación falla a menos que se aplique el modo estabilizado con piso de logaritmo ($10^{-300}$).

---

## 2. Singularidades en la Diagonal de Polarización $M(x, x)$

En la multiplicación por polarización:
$$M(x, y) = \frac{(x+y)^2 - (x-y)^2}{4}$$
Cuando $x = y$, el término diferencial $(x - y) = 0$. Al calcular $(x - y)^2 = \exp(2 \ln(x - y))$, se induce una singularidad $\ln(0)$.  
**Mitigación:** En `adaptive_evaluator.py` y `relational_glyph` se implementó una regularización analítica suave ($\text{safe\_diff} = \max(|x - y|, 10^{-15})$). Sin embargo, cerca de la diagonal, el error flotante relativo puede incrementarse si no se conmuta a precisión arbitraria.

---

## 3. Sobrecarga de Evaluación Trascendente

La evaluación de operaciones aritméticas elementales (suma, producto, división) mediante EML puro sustituye instrucciones ALU de un ciclo de reloj (e.g., `ADDSD`, `MULSD`) por múltiples evaluaciones de series de Taylor o aproximaciones Padé de $e^x$ y $\ln(y)$.
- Cada nodo EML requiere 1 función exponencial y 1 función logarítmica.
- Para una división profunda no compartida, el árbol requiere miles de evaluaciones trascendentes.
- Por tanto, EML es un **modelo teórico de unificación y expresividad canónica**, no un sustituto de aceleración de bajo nivel para cálculo numérico intensivo.

---

## 4. Desacoplamiento Semántico de Glifos Visuales

El sistema rechaza cualquier atribución histórica, mística o analógica a los glifos:
- Dos nodos con representaciones gráficas idénticas o similares pueden tener semánticas matemáticas y procedencias causales completamente disjuntas.
- Las propiedades gráficas (`visual_repr`) son proyecciones visuales auxiliares para renderizado y no influyen en el cómputo del grafo.
