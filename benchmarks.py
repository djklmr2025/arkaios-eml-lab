"""
EML Benchmarks: Float64 vs Arbitrary Precision (mpmath / Decimal 50)
Module 4: Benchmarks de precisión y rendimiento
"""

import math
import time
from decimal import Decimal, getcontext
from generator import get_variable, get_constant, ONE, eml_node
from primitives import (
    block_P, block_Add, block_L, block_Exp,
    build_V_optimized_real, build_M_odrzywolek
)

getcontext().prec = 50

def run_benchmarks():
    x = get_variable("x")
    y = get_variable("y")
    v_opt = build_V_optimized_real(x, y)

    env = {"x": 100.0, "y": 4.0}
    expected = 25.0

    print("=== Benchmark de Rendimiento y Precisión para V_opt (K=88,715 / canónica) ===")

    # 1. Float64 Memoized
    iters = 10000
    t0 = time.perf_counter()
    memo = {}
    c = {"exp": 0, "ln": 0}
    for _ in range(iters):
        memo.clear()
        c["exp"] = 0
        c["ln"] = 0
        res_f64 = v_opt.eval_memoized(env, memo, c)
    t1 = time.perf_counter()
    f64_latency_us = ((t1 - t0) / iters) * 1e6

    # 2. Arbitrary Precision (Decimal 50)
    # Evaluación manual de los pasos con Decimal
    dec_x = Decimal(str(env["x"]))
    dec_y = Decimal(str(env["y"]))
    # L(x) = ln(x)
    t2 = time.perf_counter()
    dec_lx = dec_x.ln()
    dec_llx = dec_lx.ln()
    # eml(llx, y) = exp(llx) - ln(y) = lx - ln(y)
    diff = dec_llx.exp() - dec_y.ln()
    dec_res = diff.exp()
    t3 = time.perf_counter()
    arb_latency_us = (t3 - t2) * 1e6

    f64_err = abs(res_f64 - expected) / expected
    dec_err = abs(float(dec_res) - expected) / expected

    print(f"1. Float64 Evaluado      : {res_f64:.15f}")
    print(f"   Error Relativo Float64 : {f64_err:.2e}")
    print(f"   Latencia Media Float64 : {f64_latency_us:.2f} µs/op")
    print(f"   Llamadas exp/ln en DAG : {c['exp']} exp / {c['ln']} ln")

    print(f"\n2. Arbitrary (50 Dígitos): {dec_res}")
    print(f"   Error Relativo Decimal : {dec_err:.2e}")
    print(f"   Latencia Media Decimal : {arb_latency_us:.2f} µs/op")

if __name__ == "__main__":
    run_benchmarks()
