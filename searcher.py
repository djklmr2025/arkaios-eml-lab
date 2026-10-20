"""
EML Expression Searcher and Exhaustive Sieve
Module 6: Buscador de expresiones por fuerza bruta acotada (BFS) y análisis de límites
"""

import math
from typing import List, Tuple, Dict, Set
from generator import EMLNode, get_constant, get_variable, eml_node, ONE

def run_bounded_search(target_val: float, var_env: Dict[str, float], max_depth: int = 3, tol: float = 1e-10):
    """
    Búsqueda exhaustiva acotada sobre la gramática S -> 1 | Var | eml(S, S).
    Límite combinatorio: Para profundidad D, el número de árboles posibles crece como O(C_n * 2^n).
    A profundidad 3, se evalúan miles de candidatos en milisegundos.
    A profundidad 5+, el espacio supera 10^9 estados, requiriendo podas heurísticas.
    """
    terminals = [ONE]
    for var_name in var_env.keys():
        terminals.append(get_variable(var_name))

    current_level: List[EMLNode] = list(terminals)
    all_expressions: List[EMLNode] = list(terminals)
    visited_values: Set[float] = set()

    found: List[Tuple[EMLNode, float, float]] = []

    print(f"=== Iniciando Búsqueda Exhaustiva EML (Target = {target_val}, Max Depth = {max_depth}) ===")

    for depth in range(1, max_depth + 1):
        next_level = []
        for left in all_expressions:
            for right in all_expressions:
                # Restricción: profundidad máxima
                if max(left.depth(), right.depth()) + 1 > depth:
                    continue
                node = eml_node(left, right)
                try:
                    c = {"exp": 0, "ln": 0}
                    val = node.eval_unshared(var_env, c)
                    if math.isnan(val) or math.isinf(val):
                        continue
                    round_val = round(val, 8)
                    if round_val not in visited_values:
                        visited_values.add(round_val)
                        next_level.append(node)

                        err = abs(val - target_val)
                        if err <= tol:
                            found.append((node, val, err))
                except Exception:
                    pass

        all_expressions.extend(next_level)
        print(f"   Profundidad {depth}: {len(next_level)} expresiones no-redundantes evaluadas.")

        if found:
            print(f"   [ÉXITO] {len(found)} solución(es) exacta(s) descubierta(s) a profundidad {depth}!")
            for node, val, err in found[:3]:
                print(f"     -> Expresión: {node} | K = {node.k_tokens()} | Error = {err:.2e}")
            break

    if not found:
        print(f"   [LÍMITE ALCANZADO] No se halló fórmula cerrada dentro del límite de profundidad {max_depth}.")
        print("   Nota sobre exhaustividad: Para K > 9 o Profundidad > 4, el espacio de búsqueda exige optimizadores continuos (Adam / Descenso de Coordenadas) como en Odrzywołek 2026.")

if __name__ == "__main__":
    # Buscar e^x para x = 2 (Target: e^2 ≈ 7.389056)
    run_bounded_search(target_val=math.exp(2.0), var_env={"x": 2.0}, max_depth=3)
