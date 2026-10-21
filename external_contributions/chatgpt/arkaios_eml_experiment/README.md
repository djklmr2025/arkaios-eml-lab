# Experimento ARKAIOS–EML: simplificación antes de ejecutar

Prueba una identidad exacta en matemáticas reales: `L(P(x)) = ln(exp(x)) = x`, donde `E(a,b)=exp(a)-ln(b)`, `P(x)=E(x,1)` y `L(u)=E(1,E(E(1,u),1))`.

`benchmark_eml.py` compara la evaluación literal mediante cuatro llamadas a E con la función simplificada identidad. Genera 25,000 valores reproducibles en [-3,3], calcula medianas de cinco repeticiones y errores absolutos. Requiere solo Python 3.10+.

Ejecutar en Windows: `py benchmark_eml.py`.

**Límites:** Es una prueba de concepto de eliminación de operaciones, no un compilador EML general, ni una prueba de aceleración de IA. En precisión flotante, algunas reescrituras válidas algebraicamente pueden alterar resultados o dominios; no deben aplicarse sin análisis. Los resultados dependen del equipo y del intérprete.

**Próxima etapa:** construir AST/DAG, un verificador de dominios, reglas de reescritura seguras y pruebas comparativas contra expresiones nativas y EML con optimización.
