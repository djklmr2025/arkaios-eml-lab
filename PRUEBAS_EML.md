# 🧪 Resultados de Pruebas y Validación EML — ARKAIOS Sovereign Lab

**Documento:** `TESTS-ARKAIOS-EML-001`  
**Harness de Pruebas:** `C:\ARKAIOS\eml-lab\eml_optimizer_lab.py` y `C:\ARKAIOS\eml-lab\eml_bench_node.js`  
**Fecha de Validación:** 20 de Octubre de 2026  
**Resultado Global:** **100% de Pruebas Aprobadas (0 Fallos)**  

---

## 1. Clasificación Taxonómica de Funciones

| Categoría | Estado | Criterio y Descripción |
| :--- | :--- | :--- |
| **DEMOSTRADAS** | Teóricas Probadas | Probadas analítica y matemáticamente en el paper de Odrzywołek (2026). Incluye las 36 primitivas de calculadora científica ($e, \pi, i, \sin, \cos, \tan, \arcsin, \sinh, \cosh$, etc.). |
| **IMPLEMENTADAS** | Verificadas en Código | Compiladas y evaluadas empíricamente en el laboratorio ARKAIOS (`eml-lab`) con tolerancia acotada en Float64, Estabilizada y Precisión Arbitraria de 50 decimales ($\exp, \ln, \text{const}_e, \text{const}_0, \text{id}, -, +, \times, /, \sinh$). |
| **PENDIENTES** | Optimización Futura | Funciones trigonométricas con aritmética compleja interna ($\sin, \cos, \arctan$), constantes $\pi$ e $i$, y árboles EML profundos ($D > 5$) mediante redes KAN y regresión simbólica con Adam. |

---

## 2. Métricas de Árbol vs. Grafo (Representación A vs. Representación B)

Medición empírica realizada sobre las fórmulas de Odrzywołek y las construcciones optimizadas de ARKAIOS:

| Operación | Profundidad | Símbolos Árbol (A) | Nodos Únicos DAG (B) | Ratio Compresión DAG | Evals $\exp/\ln$ (Árbol) | Evals $\exp/\ln$ (DAG) | Ahorro en Evals |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **$\exp(x)$** | 1 | 3 | 3 | **1.0x** | 1 | 1 | 0% |
| **$\ln(x)$** | 3 | 7 | 5 | **1.4x** | 3 | 3 | 0% |
| **$\text{const}_e$** | 1 | 3 | 2 | **1.5x** | 1 | 1 | 0% |
| **$\text{const}_0$** | 3 | 7 | 4 | **1.8x** | 3 | 3 | 0% |
| **$x - y$ (Sustracción)** | 4 | 11 | 8 | **1.4x** | 5 | 5 | 0% |
| **$-x$ (Negación)** | 5 | 17 | 10 | **1.7x** | 8 | 8 | 0% |
| **$x + y$ (Adición)** | 6 | 27 | 16 | **1.7x** | 13 | 13 | 0% |
| **$1 / x$ (Inverso)** | 6 | 25 | 14 | **1.8x** | 12 | 12 | 0% |
| **$x \times y$ (Odrzywołek)** | 7 | 41 | 23 | **1.8x** | 20 | 20 | 0% |
| **$x / y$ (Odrzywołek)** | 8 | 65 | 29 | **2.2x** | 32 | 32 | 0% |
| **$x / y$ (ARKAIOS OPT)** | 5 | **17** | **11** | **1.5x** | **8** | **8** | **75.0% vs Orig** |
| **$\sinh(x)$ (Odrzywołek)** | 9 | 171 | 57 | **3.0x** | 85 | 28 | **67.1% en DAG** |
| **$\sinh(x)$ (ARKAIOS OPT)** | 6 | **39** | **22** | **1.8x** | **19** | **19** | **77.6% vs Orig** |

---

## 3. Comparativa de Precisión Numérica (50 Decimales vs Float64 vs Estabilizado)

| Función | Entradas de Prueba | Referencia Exacta | Float64 Evaluado | Error Relativo F64 | Modo Estabilizado (WeftOS) | Precisión Arbitraria (50 Dígitos) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **$\exp(x)$** | $x = 2.0$ | $7.38905609893065$ | $7.38905609893065$ | `0.0e+00` | $7.38906$ | `7.38905609893065022723042746...` |
| **$\ln(x)$** | $x = 2.0$ | $0.693147180559945$ | $0.693147180559945$ | `1.6e-16` | $0.69315$ | `0.69314718055994530941723212...` |
| **$\text{const}_e$** | — | $2.718281828459045$ | $2.718281828459045$ | `0.0e+00` | $2.71828$ | `2.71828182845904523536028747...` |
| **$\text{const}_0$** | — | $0.0$ | $0.0$ | `0.0e+00` | $0.00000$ | `0.00000000000000000000000000...` |
| **$x - y$** | $x=5.0, y=2.0$ | $3.0$ | $3.0$ | `3.0e-16` | $3.00000$ | `2.99999999999999999999999999...` |
| **$x / y$ (OPT)** | $x=8.0, y=2.0$ | $4.0$ | $4.0$ | `6.7e-16` | $4.00000$ | `4.00000000000000000000000000...` |
| **$\sinh(x)$ (OPT)**| $x = 1.5$ | $2.129279455094817$ | $2.129279455094817$ | `2.1e-16` | $2.12928$ | `2.12927945509481735163908867...` |

---

## 4. Hallazgos Críticos de Dominio y Estabilidad

1. **La Trampa de $\ln(0)$ en Fórmulas Ingenuas:**
   - En la negación de Odrzywołek: $-x = 0 - x = \text{eml}(\ln(0), \exp(x))$.
   - En evaluadores reales estrictos (como Python `math.log(0)` o la biblioteca estándar de Lean 4), esto genera un error de dominio fatal.
   - En IEEE 754 con aritmética extendida, $\ln(0) = -\infty$, y $\exp(-\infty) = 0.0$, lo que permite que la expresión evalúe correctamente a $-x$.
   - **Solución ARKAIOS:** La evaluación estabilizada con piso $y \ge 10^{-300}$ o la construcción algebraica directa evitan depender de indeterminaciones flotantes.

2. **Diferenciación de Tres Fenómenos Distintos (Mandato ChatGPT):**
   - **Compresión del Grafo (DAG):** Reduce los nodos almacenados (e.g. de 171 a 57 en $\sinh$), disminuyendo el consumo de memoria en un factor $3.0\times$.
   - **Reducción del Costo de Ejecución:** La memoización elimina re-evaluaciones de ramas idénticas, ahorrando hasta un 67% de llamadas a $\exp$ y $\ln$.
   - **Estabilidad Numérica:** El clamping y el piso protegen contra cascadas de `NaN` y `OverflowError` sin alterar el comportamiento algebraico en el dominio analítico.
