# 🔬 ARKAIOS Sovereign EML Laboratory

Repositorio experimental y reproducible para investigación matemática conjunta entre **ChatGPT**, **Microsoft Copilot** y **Antigravity**.

---

## 📋 Módulos Incluidos

1. **`generator.py`**: Generador de árboles EML puros y grafos acíclicos dirigidos (DAG) con hash-consing y memoización.
2. **`primitives.py`**: Expresiones canónicas de Sub, Add, Neg, Inv, Bloques $P, Q, L$, Multiplicación ($M_{\text{orig}}$ con $K=14,471$ vs $M_{\text{opt}}$ con $K=631$) y División ($V_{\text{orig}}$ con $K=21,478,743$ vs $V_{\text{opt}}$ con $K=88,715$).
3. **`domain_tests.py`**: Pruebas de equivalencia algebraica, discontinuidades, singularidades y auditoría del fallo numérico $M(3, 3)$.
4. **`benchmarks.py`**: Pruebas de velocidad y precisión contrastando Float64 frente a Precisión Arbitraria de 50 decimales.
5. **`searcher.py`**: Buscador exhaustivo por niveles (BFS) sobre la gramática $S \to 1 \mid \text{eml}(S,S)$ con análisis de límites combinatorios.
6. **`eml_optimizer_lab.py`**: Suite comparativa integral entre Representación A (Árbol), Representación B (DAG) y Representación C (Forma Cerrada).
7. **`eml_bench_node.js`**: Implementación nativa en JavaScript/Node.js para ejecución inmediata en V8 y el puente MCP local.

---

## 🚀 Requisitos y Ejecución Rápida

### Requisitos:
- Python 3.10+ (utiliza bibliotecas estándar: `math`, `decimal`, `time`, `typing`).
- Opcional: Node.js v18+ para el harness JS.

### Ejecución de Pruebas:

```powershell
# 1. Ejecutar la suite integral de optimización
python eml_optimizer_lab.py

# 2. Auditar el caso de fallo en la diagonal M(3, 3) y equivalencias
python domain_tests.py

# 3. Correr benchmarks de precisión arbitraria (50 dígitos) y latencia
python benchmarks.py

# 4. Probar el buscador exhaustivo acotado
python searcher.py

# 5. Ejecutar la suite nativa en Node.js
node eml_bench_node.js
```

---

## 🎯 Resultados Esperados

- **Error Relativo Float64:** Inferior a $1.6 \times 10^{-16}$ (precisión a nivel de épsilon de máquina).
- **Precisión Arbitraria:** Concordancia exacta en los 50 dígitos decimales evaluados.
- **Compresión DAG:** Reducción de hasta un $70\%$ en el número de nodos y evaluaciones trascendentes redundantes.
- **División Optimizada:** Reducción comprobada de $K=21,478,743$ a $K=88,715$ tokens en forma expandida y $K=17$ en forma canónica compacta.
