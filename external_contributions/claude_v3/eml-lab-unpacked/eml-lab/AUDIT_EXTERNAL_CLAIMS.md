# Revisión de dos documentos externos (Antigravity y Copilot)

Nota: la Tabla 4 del artículo se extrajo con el formato roto; las cifras de x×y y x/y (41 / 17 y 105 / 17) deben confirmarse en el PDF.

Evidencia: `scripts/07_validate_external_claims.py` → `results/07_validate_external_claims.txt`; texto del artículo arXiv:2603.21852 (Tabla 4);
código de `github.com/djklmr2025/arkaios-eml-lab` (`adaptive_evaluator.py`, README) consultado en línea. No pude verificar los SHA-256 de descargas locales.

## A. Informe de Antigravity

| afirmación | veredicto | evidencia |
|---|---|---|
| `Exp(x)=eml(x,1)` | ✅ | trivial |
| `L(x)=eml(0,eml(x,1))=ln x` | ❌ | vale `1−x` (L(2)=−1, ln 2=0.693). La forma correcta es `E(0,E(E(0,x),1))` (el resumen de Copilot la tiene bien) |
| `Neg(z)=eml(0,eml(0,eml(z,1)))=−z` | ❌ | vale `1−ln(1−z)`, no definida para z≥1 |
| usa `0` como hoja | ⚠️ | solo se permiten `1,x,y`; el 0 cuesta K=7 (`111E1EE`) |
| Tabla, columna "Odrzywołek": Sub 11, Add 27 | ⚠️ | 11 es "búsqueda directa"; **27 es el compilador** (directa: 19) |
| Tabla, columna "Odrzywołek": M 14,471; V 21,478,743 | ❌ | **esas cifras son de nuestra construcción original**, no del artículo. Artículo: x×y = 41 (compilador) / 17 (directa); x/y = 105 / 17 |
| Columna "Claude (DAG)": Sub K=11 | ❌ | mi Sub real global es **K=19**. K=11 es `E(ln x, exp y)`, válido solo con x>0 (o con rama compleja del artículo) |
| "DAG" para K=631 / 88,715 | ❌ | son tamaños de **árbol**; el DAG tiene 59 / 180 nodos E únicos |
| Add 19, M 631, V 88,715, reducciones 95.6 % y 99.6 % | ✅ | aritmética correcta (con esa etiqueta de columna corregida) |
| División "compacta" `x/y=exp(eml(ln(ln x),y))`, K=17 | ✅ matemáticamente, ⚠️ comparación | verificada: K=17, error 1e−59 en x>1, y>0; **falla fuera de ese dominio** (x≤1, y≤0). No es comparable con la V global (21 M → 88,715); y coincide con el K=17 que el artículo ya da para x/y |
| Causa de M(3,3): polarización `((x+y)²−(x−y)²)/4`, ln(0) | ❌ | esa **no es** la construcción de K=631 (ni ninguna del paquete). En el árbol real todos los ln son >0 (400 dígitos, incluida la diagonal). El fallo es cancelación tras exponenciales anidadas |
| "Solución": piso `max(|x−y|,1e−15)`, Decimal de 50 dígitos → 9.000… | ❌ | `adaptive_evaluator.py` **no evalúa árboles EML**: `mult` usa `((x+y)**2-(x-y)**2)/4` nativo; `add` devuelve `x+y`; `_eval_arbitrary` hace `Decimal(x)*Decimal(y)`; `sub` usa `exp(ln x)-ln(exp y)` (solo x>0). El 9.0 es aritmética nativa. El árbol puro M(3,3) a 50 dígitos da 1.3e−51 y necesita ≥320 |
| `div` compacto en el evaluador | ⚠️ | `math.log(math.log(x))` lanza error para x≤1; el inspector de dominio solo revisa `y==0` y `y<0` |
| README: "error relativo float64 < 1.6e−16", "50 dígitos exactos" | ❌ | consecuencia de lo anterior: no mide EML |
| `searcher.py` BFS K≤9, prof.≤4 | ⚠️ | válido pero mucho más corto que nuestra enumeración (K≤23 exhaustivo) |
| Identificadores arXiv:2603.21852v2 y DOI 10.5281/zenodo.19183008 | ✅ | coinciden con el artículo; los hashes no los pude comprobar |

Recomendación: no tratar como resuelto el caso M(3,3) en ese repositorio hasta que el evaluador ejecute el árbol EML real (por ejemplo `eml_lab.evaluators.adaptive_eval`).

## B. Resumen de Copilot

| afirmación | veredicto |
|---|---|
| `P=E(x,1)=e^x`; `Z=E(1,E(E(1,1),1))=0`; `C(x)=E(Z,E(x,1))=1−x`; `L(x)=E(Z,E(E(Z,x),1))=ln x`; `R_a(x)=e^a−x`; `T_{a,b}(x)=x+e^a−e^b`; `D(x,y)=x−y` (x>0) | ✅ todas verificadas (álgebra + numérico); `R_a` y `T` valen en todos los reales; `L` y `D` requieren x>0 |
| "Pendientes": suma, negación, multiplicación, división globales | ⚠️ **desactualizado**: construidas y verificadas (Add19 K=19, Neg K=17, M K=631, V K=88,715; ver README §5–6) |
| "¿existe el 2? ¿existe el −1?" | ✅ respondida: `−1` K=17 (`11111EEE1EE11E1EE`), `2` K=19 (`111111EEE1EE11EE1EE`), solo con reales |
| Universalidad no demostrada | ✅ sigue siendo correcto para la clase real; el artículo la afirma para la calculadora científica con intermedios complejos (su prueba está en el SI, que no revisé) |
| Probabilidades subjetivas / "mejoras masivas para IA: no demostrado" | ✅ prudente |
