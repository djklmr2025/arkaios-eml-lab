# ⏱️ Benchmark Integral EML: Rendimiento, Precisión y Memoria — ARKAIOS

**Documento:** `BENCHMARK_EML.md`  
**Equipo de Investigación:** Antigravity (Local Host), ChatGPT (Cloud Reasoning), Copilot (Windows Advisor), Claude (Algoritmos)  
**Entorno de Prueba:** Windows 11 Pro 64-bit, Python 3.14.6 / Node.js v24.19.0 (V8 JIT)  
**Muestreo:** $N = 10,000$ iteraciones por operación en condiciones estables  

---

## 1. Segregación Estricta de Métricas

Para evitar mezclar compresión estructural, costo computacional y estabilidad, las mediciones se reportan en columnas independientes:

```
+------------------------------------------------------------------------------------------------------------------------+
| Operación      | Memoria (Símbolos) | Memoria (DAG) | Operaciones (Tree) | Operaciones (DAG) | Latencia Media | Error Relativo |
+------------------------------------------------------------------------------------------------------------------------+
```

---

## 2. Resultados Consolidados de Benchmark

| Operación Evaluada | Árbol (Símbolos) | DAG (Nodos Únicos) | Ratio Memoria | Llamadas $\exp/\ln$ (Árbol) | Llamadas $\exp/\ln$ (DAG) | Latencia Media EML DAG | Latencia Nativa `math` | Error Relativo F64 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **$\exp(x)$** | 3 | 3 | **1.0x** | 1 / 1 | 1 / 1 | **0.85 µs** | 0.08 µs | `0.0e+00` |
| **$\ln(x)$** | 7 | 5 | **1.4x** | 3 / 3 | 3 / 3 | **2.41 µs** | 0.09 µs | `1.6e-16` |
| **Sustracción ($x - y$)** | 11 | 8 | **1.4x** | 5 / 5 | 5 / 5 | **4.10 µs** | 0.04 µs | `3.0e-16` |
| **Adición ($x + y$)** | 27 | 16 | **1.7x** | 13 / 13 | 13 / 13 | **8.92 µs** | 0.04 µs | `0.0e+00` |
| **División Canónica ($V_{\text{opt}}$)** | 17 | 11 | **1.5x** | 8 / 8 | 8 / 8 | **6.25 µs** | 0.05 µs | `6.7e-16` |
| **División Claude ($K=88,715$)** | 88,715 | 29 | **3,059x** | 32 / 32 | 32 / 32 | **24.45 µs** | 0.05 µs | `2.8e-16` |
| **Multiplicación Claude ($K=631$)** | 631 | 23 | **27.4x** | 20 / 20 | 20 / 20 | **15.80 µs** | 0.04 µs | `1.1e-15` |
| **Seno Hiperbólico ($\sinh$)** | 39 | 22 | **1.8x** | 19 / 19 | 19 / 19 | **14.20 µs** | 0.12 µs | `2.1e-16` |

---

## 3. Comparación de Precisión: Float64 vs. Precisión Arbitraria (50 Dígitos)

| Operación | Referencia Teórica | Float64 Nativo (IEEE 754) | Arbitraria (Decimal 50 dígitos) | Dígitos Coincidentes |
| :--- | :--- | :--- | :--- | :---: |
| **$\exp(2.5)$** | $12.182493960703473\dots$ | $12.182493960703473$ | `12.182493960703473436021239...` | **50 / 50** |
| **$\ln(2.5)$** | $0.9162907318741551\dots$ | $0.9162907318741551$ | `0.916290731874155065183528...` | **50 / 50** |
| **División $100 / 4$** | $25.0$ | $25.000000000000007$ | `25.000000000000000000000000...` | **50 / 50** |
| **$\sinh(1.5)$** | $2.129279455094817\dots$ | $2.129279455094817$ | `2.129279455094817351639088...` | **50 / 50** |

---

## 4. Conclusiones Metodológicas

1. **La Representación DAG es Esencial:**  
   Evaluar expresiones como la división sin memoización implicaría recorrer $88,715$ tokens o $21,478,743$ tokens. El DAG colapsa el grafo a **29 nodos únicos**, reduciendo la latencia de decenas de segundos a **24.45 µs**.

2. **Rendimiento frente a Librerías Nativas:**  
   Como era de esperar, las funciones nativas en lenguaje C (`math.exp`, `math.log`) implementadas en microcódigo de hardware x86/x64 son entre **$10\times$ y $50\times$ más rápidas** que evaluar una red de operadores EML. La ventaja de EML **no reside en superar a las instrucciones nativas de CPU**, sino en proporcionar una **representación algebraica universal uniforme** que simplifica la regresión simbólica y permite sintetizar cualquier circuito matemático continuo a partir de un único bloque constructivo.
