"""
ARKAIOS Relational GLYPH Benchmark Runner
Compares:
A. Literal EML evaluation (unshared/unoptimized tree).
B. Simplified EML evaluation (optimized & memoized GLYPH DAG).
C. Conventional equivalent evaluation (native Python float64 math).

Measures:
- Latency (mean, median, stdev in microseconds)
- Batch throughput (ops/sec)
- Node count & graph depth
- Absolute & relative numerical error
- Graph construction vs optimization vs execution time separation
"""

import math
import os
import sys
import time
import tracemalloc
from typing import Any, Dict, List, Tuple

# Ensure root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from generator import get_variable, get_constant, eml_node, ONE
from primitives import block_Exp, block_Add, block_P
from relational_glyph.eml_adapter import EmlGlyphAdapter
from relational_glyph.optimizer import GlyphOptimizer


def run_benchmark(iterations: int = 5000, warmup: int = 500) -> Dict[str, Any]:
    print(f"=== Starting ARKAIOS Relational Core + GLYPH Benchmark ===")
    print(f"Warmup iterations: {warmup} | Benchmark iterations: {iterations}\n")

    # Target algebraic task: evaluate f(x) = exp(x) + (x - 1.0) at x = 1.5
    test_x = 1.5
    env = {"x": test_x}

    # Reference exact value using conventional native math:
    def conventional_eval(x: float) -> float:
        return math.exp(x) + (x - 1.0)

    ground_truth = conventional_eval(test_x)

    # -------------------------------------------------------------
    # 1. Build Representations
    # -------------------------------------------------------------
    # Representation A: Literal EML Tree
    t0_build_a = time.perf_counter()
    x_var = get_variable("x")
    c_one = get_constant(1.0)
    exp_part = block_Exp(x_var)          # exp(x)
    sub_part = block_P(x_var, c_one)     # x - 1.0
    eml_ast = block_Add(exp_part, sub_part) # exp(x) + (x - 1.0)
    graph_a = EmlGlyphAdapter.eml_to_glyph_graph(eml_ast, graph_id="graph_literal")
    t_build_a_us = (time.perf_counter() - t0_build_a) * 1e6

    # Representation B: Optimized & Simplified GLYPH Graph
    t0_build_b = time.perf_counter()
    optimizer = GlyphOptimizer()
    graph_b, opt_report = optimizer.optimize_graph(graph_a)
    t_opt_b_us = (time.perf_counter() - t0_build_b) * 1e6

    # Representation C: Conventional Function (0 build time)
    t_build_c_us = 0.0

    # -------------------------------------------------------------
    # 2. Measurement Functions
    # -------------------------------------------------------------
    def benchmark_fn(fn, args, runs, warm):
        # Warmup
        for _ in range(warm):
            fn(*args)
        # Timing
        times = []
        for _ in range(runs):
            t0 = time.perf_counter()
            res = fn(*args)
            t1 = time.perf_counter()
            times.append((t1 - t0) * 1e6)
        times.sort()
        mean_t = sum(times) / len(times)
        median_t = times[len(times) // 2]
        var = sum((x - mean_t) ** 2 for x in times) / len(times)
        stdev_t = math.sqrt(var)
        throughput = 1e6 / mean_t if mean_t > 0 else 0.0
        return mean_t, median_t, stdev_t, throughput, res

    # Benchmark A: Literal EML
    tracemalloc.start()
    mean_a, med_a, std_a, tp_a, res_a_tuple = benchmark_fn(
        EmlGlyphAdapter.evaluate_glyph_eml,
        (graph_a, graph_a.root_id, env, "stabilized"),
        iterations,
        warmup,
    )
    res_a = res_a_tuple[0]
    mem_a_current, mem_a_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Benchmark B: Simplified EML (GLYPH)
    tracemalloc.start()
    mean_b, med_b, std_b, tp_b, res_b_tuple = benchmark_fn(
        EmlGlyphAdapter.evaluate_glyph_eml,
        (graph_b, graph_b.root_id, env, "stabilized"),
        iterations,
        warmup,
    )
    res_b = res_b_tuple[0]
    mem_b_current, mem_b_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Benchmark C: Conventional Math
    tracemalloc.start()
    mean_c, med_c, std_c, tp_c, res_c = benchmark_fn(
        conventional_eval,
        (test_x,),
        iterations,
        warmup,
    )
    mem_c_current, mem_c_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Errors
    err_a_abs = abs(res_a - ground_truth)
    err_a_rel = err_a_abs / abs(ground_truth) if ground_truth != 0 else 0.0

    err_b_abs = abs(res_b - ground_truth)
    err_b_rel = err_b_abs / abs(ground_truth) if ground_truth != 0 else 0.0

    err_c_abs = abs(res_c - ground_truth)
    err_c_rel = 0.0

    results = {
        "ground_truth": ground_truth,
        "config": {"iterations": iterations, "warmup": warmup, "test_input": test_x},
        "A_literal": {
            "name": "A. Literal EML Evaluation",
            "nodes": graph_a.node_count(),
            "build_time_us": t_build_a_us,
            "mean_latency_us": mean_a,
            "median_latency_us": med_a,
            "stdev_latency_us": std_a,
            "throughput_ops_sec": tp_a,
            "peak_memory_bytes": mem_a_peak,
            "result": res_a,
            "abs_error": err_a_abs,
            "rel_error": err_a_rel,
        },
        "B_simplified": {
            "name": "B. Simplified EML Evaluation (GLYPH)",
            "nodes": graph_b.node_count(),
            "build_time_us": t_build_a_us + t_opt_b_us,
            "opt_time_us": t_opt_b_us,
            "mean_latency_us": mean_b,
            "median_latency_us": med_b,
            "stdev_latency_us": std_b,
            "throughput_ops_sec": tp_b,
            "peak_memory_bytes": mem_b_peak,
            "result": res_b,
            "abs_error": err_b_abs,
            "rel_error": err_b_rel,
            "reduction_nodes": opt_report["nodes_reduced"],
        },
        "C_conventional": {
            "name": "C. Conventional Equivalent Evaluation",
            "nodes": 1,
            "build_time_us": 0.0,
            "mean_latency_us": mean_c,
            "median_latency_us": med_c,
            "stdev_latency_us": std_c,
            "throughput_ops_sec": tp_c,
            "peak_memory_bytes": mem_c_peak,
            "result": res_c,
            "abs_error": 0.0,
            "rel_error": 0.0,
        },
    }

    # Print Summary Table
    print(f"{'Metric':<30} | {'A. Literal EML':<18} | {'B. Simplified GLYPH':<20} | {'C. Conventional':<18}")
    print("-" * 92)
    print(f"{'Nodes in Graph':<30} | {results['A_literal']['nodes']:<18} | {results['B_simplified']['nodes']:<20} | {results['C_conventional']['nodes']:<18}")
    print(f"{'Mean Latency (us)':<30} | {mean_a:<18.2f} | {mean_b:<20.2f} | {mean_c:<18.4f}")
    print(f"{'Median Latency (us)':<30} | {med_a:<18.2f} | {med_b:<20.2f} | {med_c:<18.4f}")
    print(f"{'Throughput (ops/s)':<30} | {tp_a:<18.0f} | {tp_b:<20.0f} | {tp_c:<18.0f}")
    print(f"{'Abs Error vs Reference':<30} | {err_a_abs:<18.2e} | {err_b_abs:<20.2e} | {err_c_abs:<18.2e}")
    print(f"{'Relative Error':<30} | {err_a_rel:<18.2e} | {err_b_rel:<20.2e} | {err_c_rel:<18.2e}")
    print(f"{'Peak Memory (bytes)':<30} | {mem_a_peak:<18} | {mem_b_peak:<20} | {mem_c_peak:<18}")

    return results


if __name__ == "__main__":
    run_benchmark()
