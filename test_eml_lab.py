"""
EML Comprehensive Test Suite and Benchmark Runner
Measures:
  1. Representation A (Tree) vs Representation B (DAG) node counts & symbol counts
  2. Number of exp and ln evaluations (with and without memoization)
  3. Float64 vs Stabilized vs Arbitrary precision (50 decimals)
  4. Accuracy on elementary functions: exp, ln, sub, add, mult, div, sinh
  5. Comparisons with Odrzywolek 2026 paper
"""

import math
from decimal import Decimal
from eml_engine import (
    EmlMetrics, VariableNode, ConstantNode, ONE,
    eml_exp, eml_ln, eml_const_e, eml_const_zero,
    eml_sub, eml_div_log, eml_div_general, eml_mult_log, eml_sinh, eml_identity,
    EML
)

def run_suite():
    x = VariableNode("x")
    y = VariableNode("y")

    functions = {
        "exp(x)": (eml_exp(x), {"x": 2.5}, lambda env: math.exp(env["x"]), "x in R"),
        "ln(x)": (eml_ln(x), {"x": 2.5}, lambda env: math.log(env["x"]), "x > 0"),
        "const_e": (eml_const_e(), {}, lambda env: math.e, "constant"),
        "const_zero": (eml_const_zero(), {}, lambda env: 0.0, "constant"),
        "id(x)": (eml_identity(x), {"x": 3.14159}, lambda env: env["x"], "x in R"),
        "sub(x, y) [x - y]": (eml_sub(x, y), {"x": 7.5, "y": 2.5}, lambda env: env["x"] - env["y"], "x > 0, y in R"),
        "div_log(x, y) [x / y]": (eml_div_log(x, y), {"x": 9.0, "y": 3.0}, lambda env: env["x"] / env["y"], "x > 1, y > 0"),
        "div_general(x, y) [x / y]": (eml_div_general(x, y), {"x": 9.0, "y": 3.0}, lambda env: env["x"] / env["y"], "x > 0, y > 0"),
        "mult_log(x, y) [x * y]": (eml_mult_log(x, y), {"x": 4.0, "y": 3.0}, lambda env: env["x"] * env["y"], "x > 1, y > 0"),
        "sinh(x)": (eml_sinh(x), {"x": 1.5}, lambda env: math.sinh(env["x"]), "x in R"),
    }

    print("=" * 105)
    print(f"{'Función':<25} | {'Depth':<5} | {'Tree Symb':<9} | {'DAG Nodes':<9} | {'Tree Exp/Ln':<11} | {'DAG Exp/Ln':<10} | {'Rel Error (F64)':<15} | {'Arbitrary Prec (50d)'}")
    print("=" * 105)

    results = []

    for name, (expr, env, ref_fn, domain) in functions.items():
        tree_symbols = expr.total_symbols()
        depth = expr.depth()
        dag_nodes = len(expr.collect_unique_nodes())

        # Evaluate on Tree
        m_tree = EmlMetrics()
        val_tree = expr.eval_tree(env, m_tree, mode="float64")

        # Evaluate on DAG
        m_dag = EmlMetrics()
        memo = {}
        val_dag = expr.eval_dag(env, memo, m_dag, mode="float64")

        # Evaluate Stabilized
        m_stab = EmlMetrics()
        val_stab = expr.eval_tree(env, m_stab, mode="stabilized")

        # Evaluate Arbitrary Precision
        m_arb = EmlMetrics()
        val_arb = expr.eval_tree(env, m_arb, mode="arbitrary")

        # Reference ground truth
        ref_val = ref_fn(env)
        rel_err = abs(val_tree - ref_val) / max(1e-15, abs(ref_val))

        print(f"{name:<25} | {depth:<5} | {tree_symbols:<9} | {dag_nodes:<9} | {m_tree.exp_evals:<11} | {m_dag.exp_evals:<10} | {rel_err:<15.2e} | {str(val_arb)[:18]}...")

        results.append({
            "name": name,
            "depth": depth,
            "tree_symbols": tree_symbols,
            "dag_nodes": dag_nodes,
            "tree_evals": m_tree.exp_evals,
            "dag_evals": m_dag.exp_evals,
            "rel_err": rel_err,
            "val_f64": val_tree,
            "val_stab": val_stab,
            "val_arb": str(val_arb),
            "ref_val": ref_val,
            "domain": domain
        })

    print("=" * 105)
    return results

if __name__ == "__main__":
    run_suite()
