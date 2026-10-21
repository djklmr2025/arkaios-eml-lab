# Informe Comparativo de Contribuciones: ChatGPT vs. Claude

**Proyecto:** ARKAIOS–EML Experimental Laboratory  
**Responsable de Verificación:** Antigravity / Elemia  
**Fecha:** 2026-10-20  
**Rama:** `experimental/eml-glyph`  
**Estado:** `EMPIRICALLY_VERIFIED` (Auditoría Criptográfica y Ejecución Aprobadas)  

---

## 1. Verificación Criptográfica de Integridad (SHA-256)

Se contrastaron los archivos originales alojados en el Escritorio del usuario con las copias resguardadas en la bóveda de fuentes [`sources/`](file:///c:/ARKAIOS/eml-lab/sources/):

| Contribución | Archivo Escritorio | Archivo en `eml-lab/sources/` | Hash SHA-256 (Ambos) | Integridad Byte a Byte |
| :--- | :--- | :--- | :--- | :--- |
| **ChatGPT** | `ARKAIOS_EML_Experimento_Simplificacion.zip` | `ARKAIOS_EML_Experimento_Simplificacion_ChatGPT.zip` | `B5211833D0BFFA4A88D45C308F422C6EC20682DC8DC9CF9C936C49056FA7EA2D` | **100% MATCH (Idéntico)** |
| **Claude** | `ARKAIOS_EML_Experimento_Simplificacion 2.zip` | `ARKAIOS_EML_Experimento_Simplificacion_Claude.zip` | `48E03A13937562A91389D4BD187BC84DC670C8C83F9C0A9EC8E5DE838D26716D` | **100% MATCH (Idéntico)** |

> **Dictamen de Almacenamiento:** Los archivos en `sources/` son idénticos byte a byte a los originales. El usuario puede retirar o borrar los ZIPs del Escritorio con absoluta seguridad cuando lo considere oportuno.

---

## 2. Ejecución y Resultados del Aporte de ChatGPT

- **Directorio de Trabajo:** [`external_contributions/chatgpt/arkaios_eml_experiment/`](file:///c:/ARKAIOS/eml-lab/external_contributions/chatgpt/arkaios_eml_experiment/)
- **Script Auditado:** `benchmark_eml.py`
- **Hipótesis Probada:** Simplificación simbólica de la identidad $L(P(x)) = \ln(\exp(x)) = x$.
- **Resultados de la Ejecución:**
  * Muestras Evaluadas: 25,000 puntos pseudoaleatorios en $[-3, 3]$ (semilla `20261020`).
  * Tiempo EML Compuesto (mediana): $114.661\,\text{ms}$ (4 llamadas EML por punto).
  * Tiempo Simplificado (mediana): $12.978\,\text{ms}$ (0 llamadas EML, identidad nativa).
  * Factor de Aceleración: **$8.84\times$**.
  * Error Absoluto Máximo: **$4.44 \times 10^{-16}$** (acorde al épsilon de máquina en float64).
  * Discrepancia de Checksums: $0.00$.

---

## 3. Ejecución y Resultados del Aporte de Claude

- **Directorio de Trabajo:** [`external_contributions/claude/eml-lab-unpacked/eml-lab/`](file:///c:/ARKAIOS/eml-lab/external_contributions/claude/eml-lab-unpacked/eml-lab/)
- **Entorno de Ejecución:** `C:\ARKAIOS\.venv` con `mpmath 1.4.1` instalado.
- **Resultados de Pruebas Unitarias (`tests/test_core.py`):** **6/6 pruebas aprobadas en 1.833 s**.

### Tabla Comparativa de Complejidad ($K$ Tokens y Nodos DAG)
Resultados obtenidos mediante `scripts/01_counts.py`:

| Operación | Complejidad Árbol ($K$) | Profundidad | Nodos E (Árbol) | Nodos Únicos E (DAG) | Entradas $x$ / $y$ |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Suma Original (`Add_orig`)** | 139 | 13 | 69 | 21 | 1 / 9 |
| **Suma Optimizada (`Add19`)** | **19** | 8 | 9 | **9** | 3 / 1 |
| **Resta Original (`Sub_orig`)** | 31 | 7 | 15 | 12 | 1 / 3 |
| **Resta Optimizada (`Sub19`)** | **19** | 6 | 9 | **9** | 1 / 3 |
| **Multiplicación Original (`M_orig`)** | 14,471 | 37 | 7,235 | 107 | 76 / 468 |
| **Multiplicación Optimizada (`M_opt`)** | **631** | 24 | 315 | **59** | 60 / 26 |
| **División Original (`V_orig`)** | 21,478,743 | 82 | 10,739,371 | 284 | 5,776 / 799,344 |
| **División Optimizada (`V_opt`)** | **88,715** | 58 | 44,357 | **180** | 3,600 / 8,268 |

### Validación Multi-Precisión (`scripts/03_verify_mp.py`):
* `Add19` / `Sub19`: 196 pares en $[-30, 30]^2$, 0 fallos de dominio, peor error absoluto $5.63 \times 10^{-388}$.
* `M_opt` ($K=631$): 81 pares en $[-3, 3]^2$, 0 fallos de dominio, precisión adaptativa hasta 418 dígitos, peor error $3.87 \times 10^{-119}$.
* `V_opt` ($K=88,715$): 42 pares con dominios mixtos (positivos, negativos, cero), 0 fallos de dominio, peor error $2.48 \times 10^{-119}$.

---

## 4. Hallazgos Científicos y Correcciones de la Auditoría Cruzada

Claude aportó correcciones rigurosas en [`AUDIT_EXTERNAL_CLAIMS.md`](file:///c:/ARKAIOS/eml-lab/external_contributions/claude/AUDIT_EXTERNAL_CLAIMS.md):

1. **Corrección de la Primitiva de Logaritmo:**
   - La expresión simplificada $E(0, E(x, 1)) = e^0 - \ln(e^x - 0) = 1 - x$, por lo que es la reflexión $C(x) = 1 - x$, no $\ln(x)$.
   - La forma pura en la gramática $\{1, E\}$ requiere generar primero el cero $Z = E(1, E(E(1, 1), 1))$ ($K=7$) y luego calcular $L(x) = E(Z, E(E(Z, x), 1)) = \ln(x)$.
2. **Constantes Fundamentales Descubiertas en Gramática Pura $\{1, E\}$:**
   - Cero ($0$): `111E1EE` ($K=7$)
   - Menos uno ($-1$): `11111EEE1EE11E1EE` ($K=17$)
   - Dos ($2$): `111111EEE1EE11EE1EE` ($K=19$)
3. **Causa Raíz de la Inestabilidad Numérica en $M(3, 3)$:**
   - En el árbol real $M_{\text{opt}}$ ($K=631$), los argumentos de los logaritmos son estrictamente positivos (no hay división por cero ni $\ln(0)$).
   - El fallo numérico observado en punto flotante tradicional es una **cancelación catastrófica** derivada de torres exponenciales anidadas. Requiere una precisión adaptativa de $\ge 320$ dps en `mpmath` para estabilizarse analíticamente.

---

## 5. Cuadro Comparativo General

| Aspecto | Contribución de ChatGPT | Contribución de Claude |
| :--- | :--- | :--- |
| **Enfoque Principal** | Simplificación preliminar y microbenchmark demostrativo | Reducción combinatoria exhaustiva, DAGs globales y auditoría de precisión |
| **Expresiones Analizadas** | Identidad $\ln(\exp(x)) = x$ | Suma ($K=19$), Resta ($K=19$), Producto ($K=631$), División ($K=88,715$) |
| **Alcance Numérico** | Float64 estándar en Python | Float64 + Precisión arbitraria hasta 418 dps (`mpmath`) |
| **Mapeo DAG** | Conceptual | Grafos JSON y RPN formalizados con conteo exacto de nodos únicos |
| **Auditoría de Reclamaciones** | Orientada a límites y directivas de diseño | Auditoría crítica matemática línea por línea |
