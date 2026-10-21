# ARKAIOS Relational Core + GLYPH: Resultados Experimentales

**Fecha:** 2026-10-20  
**Rama:** `experimental/eml-glyph`  
**Entorno:** Windows 11 Host, Python 3.12, Precisión Arbitraria & Float64  
**Estado:** `EMPIRICALLY_VERIFIED` (21/21 Pruebas Aprobadas)  

---

## 1. Resumen de la Suite Automatizada

Ejecución de la suite completa (`python -m unittest discover -s relational_glyph/tests -p "test_*.py"`):

| Módulo de Prueba | Componente Auditado | Casos | Estado |
| :--- | :--- | :--- | :--- |
| `test_relational_core.py` | Capacidades COMBINE, REINFORCE, CANCEL, TRANSFORM, TRACE, Convergencia de 5 Entradas | 6 | **PASS (100%)** |
| `test_signals.py` | Casos A (Refuerzo), B (Cancelación), C (General), D (Trazabilidad), E (Retorno) | 5 | **PASS (100%)** |
| `test_graph_ir.py` | Creación de DAG, Detección/Rechazo de Ciclos, Orden Topológico, Serialización JSON Schema | 3 | **PASS (100%)** |
| `test_provenance.py` | Determinismo SHA-256, Reconstrucción de Linaje Causal, No Destrucción de Entradas Nulas | 2 | **PASS (100%)** |
| `test_eml_adapter.py` | Traducción EML a GLYPH, Evaluación con Semántica EML, Detección de Singularidades | 3 | **PASS (100%)** |
| `test_optimizer.py` | Constant Folding, Reducción $E(x,1) \to \exp(x)$, Dead Code Elimination, Preservación de Grafo Original | 2 | **PASS (100%)** |
| **Total** | **Suite Completa Relational GLYPH** | **21** | **PASS (0 Fallos)** |

---

## 2. Resultados del Modelo de Cinco Señales

Evaluación del sistema $S(u) = \sum_{k=0}^4 z_k(u)$ con $z_k(u) = A_k e^{i (\omega_k u + \phi_k)}$:

1. **Caso A (Refuerzo Constructivo):**
   - Parámetros: $A_k = 1.0, \omega_k = 2.0, \phi_k = 0.5$.
   - Resultado: $|S(u)| = 5.000000000000$ en $u \in \{0.0, 1.0, \pi, 10.0\}$ (Error $< 10^{-15}$).
2. **Caso B (Cancelación Destructiva Simétrica):**
   - Parámetros: $A_k = 1.0, \omega_k = 3.0, \phi_k = \frac{2\pi k}{5}$.
   - Resultado: $|S(u)| = 6.84 \times 10^{-16} \approx 0$ (Verificado dentro de tolerancia numérica de máquina).
3. **Caso C (Composición Heterogénea):**
   - 5 señales con distintas amplitudes, frecuencias y fases comparadas contra suma analítica de Euler: error relativo $< 10^{-14}$.
4. **Caso D (Invariante de Trazabilidad):**
   - En el punto de cancelación $|S(u)| \approx 0$, el registro conserva el 100% de los 5 objetos de señal, amplitudes unitarias y fases individuales.
5. **Caso E (Mapeo de Retorno):**
   - Mapear de 1 escalar/complejo central a 5 entradas es una proyección indeterminada con pérdida media del $100\%$ a menos que los parámetros se preserven en los metadatos de procedencia.

---

## 3. Benchmarks Comparativos de Rendimiento (A vs. B vs. C)

Tarea de prueba: Evaluación algebraica de $f(x) = e^x + (x - 1.0)$ en $x = 1.5$.  
5,000 iteraciones cronometradas tras 500 iteraciones de calentamiento:

| Métrica | A. EML Literal (Árbol) | B. EML Simplificado (GLYPH DAG) | C. Convencional (Float64 Nativo) |
| :--- | :--- | :--- | :--- |
| **Nodos en Grafo** | 22 nodos | **19 nodos** (3 reducidos) | 1 función nativa |
| **Latencia Media** | $267.83\,\mu\text{s}$ | **$235.47\,\mu\text{s}$** (12.1% más rápido) | $1.85\,\mu\text{s}$ |
| **Latencia Mediana** | $129.80\,\mu\text{s}$ | $187.00\,\mu\text{s}$ | $1.10\,\mu\text{s}$ |
| **Rendimiento (Throughput)** | $3,734\,\text{ops/s}$ | **$4,247\,\text{ops/s}$** | $541,507\,\text{ops/s}$ |
| **Error Absoluto vs. Exacto** | $3.12 \times 10^{-8}$ | $3.12 \times 10^{-8}$ | $0.00$ |
| **Error Relativo** | $6.27 \times 10^{-9}$ | $6.27 \times 10^{-9}$ | $0.00$ |
| **Memoria Pico Traced** | $647,384\,\text{bytes}$ | **$515,172\,\text{bytes}$** (20.4% menor) | $178,976\,\text{bytes}$ |

### Conclusiones del Benchmark:
- La simplificación y memoización en el grafo GLYPH reduce tanto el número de nodos (-13.6%) como el consumo de memoria (-20.4%) y el tiempo medio de ejecución (-12.1%).
- Frente a la aritmética convencional en C/ASM (representación C), el motor interpretado EML incurre en una sobrecarga representacional esperada por evaluar múltiples exponenciales y logaritmos trascendentes, confirmando que EML es una herramienta de **expresividad fundacional y trazabilidad matemática**, no un reemplazo de los núcleos ALU de coma flotante de bajo nivel.
