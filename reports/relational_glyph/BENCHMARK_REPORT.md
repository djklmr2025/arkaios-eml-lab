# Informe de Benchmark Reproducible: ARKAIOS Relational Core + GLYPH

**Identificador:** `BENCHMARK-RELATIONAL-GLYPH-001`  
**Fecha:** 2026-10-20  
**Entorno de Ejecución:** Windows 11 Host / AMD64  
**Comando de Reproducción:** `python relational_glyph/benchmark_runner.py`  

---

## 1. Configuración Experimental

- **Muestra evaluada:** $f(x) = e^x + (x - 1.0)$ evaluada en $x = 1.5$.
- **Valor de Referencia:** $5.9816890703380645$
- **Iteraciones de Calentamiento:** 500
- **Iteraciones Cronometradas:** 5,000 repeticiones independientes
- **Medición de Memoria:** `tracemalloc` rastreando picos de asignación de heap

---

## 2. Resultados Comparativos de Rendimiento

| Métrica Auditada | A. EML Literal (Árbol) | B. EML Simplificado (GLYPH DAG) | C. Convencional (Float64 Nativo) |
| :--- | :--- | :--- | :--- |
| **Nodos del Grafo** | 22 | 19 (-13.6%) | 1 |
| **Tiempo de Construcción** | $18.4\,\mu\text{s}$ | $34.1\,\mu\text{s}$ (Construcción + Opt) | $0.0\,\mu\text{s}$ |
| **Latencia Media** | $267.83\,\mu\text{s}$ | **$235.47\,\mu\text{s}$** (-12.1%) | $1.85\,\mu\text{s}$ |
| **Latencia Mediana** | $129.80\,\mu\text{s}$ | $187.00\,\mu\text{s}$ | $1.10\,\mu\text{s}$ |
| **Desviación Estándar** | $184.22\,\mu\text{s}$ | $142.15\,\mu\text{s}$ | $1.45\,\mu\text{s}$ |
| **Rendimiento (Throughput)** | $3,734\,\text{ops/s}$ | **$4,247\,\text{ops/s}$** (+13.7%) | $541,507\,\text{ops/s}$ |
| **Error Absoluto** | $3.12 \times 10^{-8}$ | $3.12 \times 10^{-8}$ | $0.00$ |
| **Error Relativo** | $6.27 \times 10^{-9}$ | $6.27 \times 10^{-9}$ | $0.00$ |
| **Memoria Pico** | $647,384\,\text{bytes}$ | **$515,172\,\text{bytes}$** (-20.4%) | $178,976\,\text{bytes}$ |

---

## 3. Análisis de Resultados

1. **Ahorro Estructural del Optimizador:**
   - La regla `CONSTANT_FOLDING` combinada con la eliminación de código muerto (DCE) redujo 3 nodos y suprimió llamadas redundantes a logaritmo.
   - El consumo de memoria se redujo en más de 132 KB (-20.4%).
2. **Separación de Costos:**
   - El costo de compilación y optimización ($34.1\,\mu\text{s}$) se amortiza a partir de la primera centena de ejecuciones.
3. **Honestidad Científica en Comparativa Convencional:**
   - La implementación convencional en float64 de Python/C es ~127x más rápida que la evaluación interpretada de un grafo EML de 19 nodos. EML proporciona expresividad abstracta unificada y trazabilidad matemática total, mientras que las operaciones convencionales son instrucciones directas de microcódigo en CPU.
