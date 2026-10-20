"""
EML Domain and Algebraic Equivalence Tests
Module 3: Pruebas de dominios, singularidades y caso de fallo numérico M(3, 3)
"""

import math
from generator import get_variable, get_constant, ONE
from primitives import (
    block_P, block_Add, block_L, block_Exp,
    build_M_odrzywolek, build_M_optimized_real,
    build_V_odrzywolek, build_V_optimized_real
)

def test_m33_failure_case():
    """
    Auditoría del caso de fallo numérico M(3, 3):
    En la multiplicación por polarización quarter-square:
       M(x, y) = ((x + y)^2 - (x - y)^2) / 4
    Cuando x = y (e.g. x = 3, y = 3):
       (x - y) = (3 - 3) = 0
    Al computar el término logarítmico L(x - y):
       L(0) = ln(0) -> -inf (en IEEE 754) o ValueError (en Python math.log).
    """
    x = get_variable("x")
    y = get_variable("y")
    m_opt = build_M_optimized_real(x, y)

    env_diag = {"x": 3.0, "y": 3.0}
    env_non_diag = {"x": 3.0, "y": 2.0}

    print("=== Caso de Fallo Numérico M(3, 3) ===")
    print("1. Evaluando punto fuera de la diagonal M(3, 2):")
    c_ok = {"exp": 0, "ln": 0}
    memo_ok = {}
    res_ok = m_opt.eval_memoized(env_non_diag, memo_ok, c_ok)
    print(f"   Resultado M(3, 2) = {res_ok:.4f} (Esperado: 6.0, Error: {abs(res_ok - 6.0):.2e})")

    print("\n2. Evaluando punto diagonal M(3, 3):")
    c_fail = {"exp": 0, "ln": 0}
    memo_fail = {}
    try:
        res_fail = m_opt.eval_memoized(env_diag, memo_fail, c_fail)
        print(f"   Resultado M(3, 3): {res_fail}")
    except ValueError as e:
        print(f"   [FALLO DETECTADO] Error de dominio esperado: {e}")
        print("   Explicación Matemática: (3 - 3) = 0; el operador EML requiere argumento estrictamente positivo para ln(y).")

def test_algebraic_equivalence():
    x = get_variable("x")
    y = get_variable("y")

    v_opt = build_V_optimized_real(x, y)
    test_points = [
        {"x": 10.0, "y": 2.0, "expected": 5.0},
        {"x": 9.0, "y": 3.0, "expected": 3.0},
        {"x": 12.0, "y": 4.0, "expected": 3.0},
        {"x": 100.0, "y": 25.0, "expected": 4.0},
    ]

    print("\n=== Prueba de Equivalencia Algebraica para División Optimizada V_opt(x, y) ===")
    for pt in test_points:
        env = {"x": pt["x"], "y": pt["y"]}
        memo = {}
        c = {"exp": 0, "ln": 0}
        val = v_opt.eval_memoized(env, memo, c)
        err = abs(val - pt["expected"])
        print(f"   V({pt['x']}, {pt['y']}) = {val:.8f} | Esperado: {pt['expected']:.8f} | Error: {err:.2e}")

if __name__ == "__main__":
    test_m33_failure_case()
    test_algebraic_equivalence()
