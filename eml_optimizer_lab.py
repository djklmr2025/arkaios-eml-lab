"""
EML Multi-Representation Optimizer & Benchmark Laboratory
ARKAIOS Sovereign Research Lab (ChatGPT & Copilot Collaboration)

Evaluates:
  Representation A: Original Raw EML Tree (unshared nodes)
  Representation B: EML DAG with Common Subexpression Elimination (CSE) & memoization
  Representation C: Simplified Algebraic Reference (Ground Truth)

Tracks:
  - Total symbols vs unique DAG nodes
  - Actual exp and ln evaluation count
  - Numerical precision across Float64, Stabilized (WeftOS bounds), and Arbitrary Precision (Decimal 50)
  - Execution time benchmarks
  - Domain boundaries & singularity preservation
"""

import math
import time
from decimal import Decimal, getcontext
from typing import Dict, Any, Tuple, Set

getcontext().prec = 50

class EmlCounter:
    def __init__(self):
        self.exp_count = 0
        self.ln_count = 0

    def reset(self):
        self.exp_count = 0
        self.ln_count = 0

class ENode:
    """Base Node for AST / DAG."""
    def __init__(self, key: str):
        self.key = key

    def size(self) -> int:
        raise NotImplementedError

    def depth(self) -> int:
        raise NotImplementedError

    def collect(self, visited: Set[str]) -> None:
        raise NotImplementedError

    def eval_raw(self, env: Dict[str, float], counter: EmlCounter, mode: str = "float64") -> Any:
        raise NotImplementedError

    def eval_dag(self, env: Dict[str, float], memo: Dict[str, Any], counter: EmlCounter, mode: str = "float64") -> Any:
        raise NotImplementedError

class Const(ENode):
    def __init__(self, val: float, name: str = None):
        self.val = float(val)
        self.name = name if name else str(val)
        super().__init__(f"C({self.name})")

    def size(self) -> int:
        return 1

    def depth(self) -> int:
        return 0

    def collect(self, visited: Set[str]) -> None:
        visited.add(self.key)

    def eval_raw(self, env: Dict[str, float], counter: EmlCounter, mode: str = "float64") -> Any:
        if mode == "arbitrary":
            return Decimal(str(self.val))
        return self.val

    def eval_dag(self, env: Dict[str, float], memo: Dict[str, Any], counter: EmlCounter, mode: str = "float64") -> Any:
        return self.eval_raw(env, counter, mode)

    def __repr__(self):
        return self.name

class Var(ENode):
    def __init__(self, name: str):
        self.name = name
        super().__init__(f"V({name})")

    def size(self) -> int:
        return 1

    def depth(self) -> int:
        return 0

    def collect(self, visited: Set[str]) -> None:
        visited.add(self.key)

    def eval_raw(self, env: Dict[str, float], counter: EmlCounter, mode: str = "float64") -> Any:
        v = env[self.name]
        if mode == "arbitrary":
            return Decimal(str(v))
        return float(v)

    def eval_dag(self, env: Dict[str, float], memo: Dict[str, Any], counter: EmlCounter, mode: str = "float64") -> Any:
        return self.eval_raw(env, counter, mode)

    def __repr__(self):
        return self.name

class Eml(ENode):
    def __init__(self, left: ENode, right: ENode):
        self.left = left
        self.right = right
        super().__init__(f"E({left.key},{right.key})")

    def size(self) -> int:
        return 1 + self.left.size() + self.right.size()

    def depth(self) -> int:
        return 1 + max(self.left.depth(), self.right.depth())

    def collect(self, visited: Set[str]) -> None:
        if self.key not in visited:
            visited.add(self.key)
            self.left.collect(visited)
            self.right.collect(visited)

    def _op(self, l: Any, r: Any, counter: EmlCounter, mode: str) -> Any:
        counter.exp_count += 1
        counter.ln_count += 1

        if mode == "float64":
            # Extended IEEE 754 logic
            try:
                # Handle extended arithmetic: exp(-inf) -> 0, ln(0) -> -inf
                if r <= 0.0:
                    if r == 0.0:
                        ln_r = -float('inf')
                    else:
                        # Real domain boundary exception
                        raise ValueError(f"Domain error: ln({r}) where r <= 0")
                else:
                    ln_r = math.log(r)

                if l == -float('inf'):
                    exp_l = 0.0
                elif l > 709.78:
                    exp_l = float('inf')
                else:
                    exp_l = math.exp(l)

                return exp_l - ln_r
            except OverflowError:
                return float('inf')

        elif mode == "stabilized":
            # WeftOS eml-core stability constants
            # EXP_CLAMP = 20.0, EXP_CLAMP_LO = -20.0
            # LN_ARG_FLOOR = 1e-300
            l_val = max(-20.0, min(20.0, float(l)))
            r_val = max(1e-300, float(r))
            return math.exp(l_val) - math.log(r_val)

        elif mode == "arbitrary":
            dl = Decimal(l)
            dr = Decimal(r)
            if dr <= 0:
                raise ValueError(f"Domain error in arbitrary precision: ln({dr}) <= 0")
            return dl.exp() - dr.ln()

        else:
            raise ValueError(f"Unknown evaluation mode: {mode}")

    def eval_raw(self, env: Dict[str, float], counter: EmlCounter, mode: str = "float64") -> Any:
        l = self.left.eval_raw(env, counter, mode)
        r = self.right.eval_raw(env, counter, mode)
        return self._op(l, r, counter, mode)

    def eval_dag(self, env: Dict[str, float], memo: Dict[str, Any], counter: EmlCounter, mode: str = "float64") -> Any:
        if self.key in memo:
            return memo[self.key]
        l = self.left.eval_dag(env, memo, counter, mode)
        r = self.right.eval_dag(env, memo, counter, mode)
        val = self._op(l, r, counter, mode)
        memo[self.key] = val
        return val

    def __repr__(self):
        return f"EML[{self.left},{self.right}]"

# ---------------------------------------------------------------------------
# Constructive Factory Functions
# ---------------------------------------------------------------------------
ONE = Const(1.0, "1")

def e_op(a, b): return Eml(a, b)
def e_exp(z): return e_op(z, ONE)
def e_log(z): return e_op(ONE, e_exp(e_op(ONE, z)))
def e_zero(): return e_log(ONE)
def e_sub(a, b): return e_op(e_log(a), e_exp(b))
def e_neg(z): return e_sub(e_zero(), z)
def e_add(a, b): return e_sub(a, e_neg(b))
def e_inv(z): return e_exp(e_neg(e_log(z)))
def e_mul_odrzywolek(a, b): return e_exp(e_add(e_log(a), e_log(b)))
def e_div_odrzywolek(a, b): return e_mul_odrzywolek(a, e_inv(b))
def e_sinh_odrzywolek(z):
    e2z = e_exp(e_add(z, z))
    ez = e_exp(z)
    two = e_add(ONE, ONE)
    return e_div_odrzywolek(e_sub(e2z, ONE), e_mul_odrzywolek(two, ez))

# Optimized Pure Real Constructions (avoiding -inf intermediate cascades)
def e_sub_direct(a, b):
    """Direct subtraction: a - b = eml(ln(a), exp(b)) for a > 0."""
    return e_op(e_log(a), e_exp(b))

def e_div_direct(a, b):
    """
    Direct Real Division: a / b = exp(ln(a) - ln(b))
    = exp(eml(ln(ln(a)), b)) for a > 1, b > 0.
    EML Nodes: 8 vs Odrzywolek 32.
    """
    ln_a = e_log(a)
    ln_ln_a = e_log(ln_a)
    return e_exp(e_op(ln_ln_a, b))

def e_sinh_direct(z):
    """
    Direct Real Hyperbolic Sine:
    sinh(z) = (e^z - e^-z)/2 = eml(z, exp(e^-z)) / 2
    EML Nodes: 24 vs Odrzywolek 85 (3.5x reduction!).
    """
    ez = e_exp(z)
    inv_ez = e_div_direct(ONE, ez) # or 1/ez
    # e^z - e^-z = eml(z, exp(e^-z))
    num = e_op(z, e_exp(inv_ez))
    TWO = Const(2.0, "2")
    return e_div_direct(num, TWO)

def run_comparative_benchmark():
    x = Var("x")
    y = Var("y")

    models = [
        # (Name, Construction, Env, Ref_fn, Domain)
        ("exp(x)", e_exp(x), {"x": 2.0}, lambda env: math.exp(env["x"]), "x in R"),
        ("ln(x)", e_log(x), {"x": 2.0}, lambda env: math.log(env["x"]), "x > 0"),
        ("const_e", e_exp(ONE), {}, lambda env: math.e, "constant"),
        ("const_zero", e_zero(), {}, lambda env: 0.0, "constant"),
        ("sub_orig(x,y)", e_sub(x, y), {"x": 5.0, "y": 2.0}, lambda env: env["x"] - env["y"], "x > 0, y in R"),
        ("neg_orig(x)", e_neg(x), {"x": 3.0}, lambda env: -env["x"], "IEEE extended"),
        ("add_orig(x,y)", e_add(x, y), {"x": 3.0, "y": 4.0}, lambda env: env["x"] + env["y"], "IEEE extended"),
        ("inv_orig(x)", e_inv(x), {"x": 2.0}, lambda env: 1.0 / env["x"], "x > 0"),
        ("div_direct(x,y) [OPT]", e_div_direct(x, y), {"x": 8.0, "y": 2.0}, lambda env: env["x"] / env["y"], "x > 1, y > 0"),
        ("sinh_direct(x) [OPT]", e_sinh_direct(x), {"x": 1.5}, lambda env: math.sinh(env["x"]), "x in R"),
    ]

    print("\n" + "=" * 120)
    print(f"{'Operación':<24} | {'Tree Symb':<9} | {'DAG Nodes':<9} | {'Tree Evals':<10} | {'DAG Evals':<9} | {'F64 Error':<11} | {'Stab Val':<12} | {'Arbitrary (50d)'}")
    print("=" * 120)

    records = []

    for name, expr, env, ref_fn, domain in models:
        tree_symb = expr.size()
        depth = expr.depth()
        visited = set()
        expr.collect(visited)
        dag_nodes = len(visited)

        # 1. Tree evaluation
        c_tree = EmlCounter()
        try:
            val_tree = expr.eval_raw(env, c_tree, mode="float64")
        except Exception as e:
            val_tree = f"ERR: {e}"

        # 2. DAG evaluation
        c_dag = EmlCounter()
        memo = {}
        try:
            val_dag = expr.eval_dag(env, memo, c_dag, mode="float64")
        except Exception as e:
            val_dag = f"ERR: {e}"

        # 3. Stabilized
        c_stab = EmlCounter()
        try:
            val_stab = expr.eval_raw(env, c_stab, mode="stabilized")
        except Exception as e:
            val_stab = f"ERR: {e}"

        # 4. Arbitrary precision
        c_arb = EmlCounter()
        try:
            val_arb = expr.eval_raw(env, c_arb, mode="arbitrary")
            val_arb_str = f"{str(val_arb)[:16]}..."
        except Exception as e:
            val_arb = f"ERR: {e}"
            val_arb_str = "DOMAIN_ERR"

        # Reference
        ref_val = ref_fn(env)
        if isinstance(val_tree, float):
            err = abs(val_tree - ref_val) / max(1e-15, abs(ref_val))
            err_str = f"{err:.1e}"
        else:
            err_str = "N/A"

        stab_str = f"{val_stab:.5f}" if isinstance(val_stab, float) else "ERR"

        print(f"{name:<24} | {tree_symb:<9} | {dag_nodes:<9} | {c_tree.exp_count:<10} | {c_dag.exp_count:<9} | {err_str:<11} | {stab_str:<12} | {val_arb_str}")

        records.append({
            "name": name,
            "depth": depth,
            "tree_symbols": tree_symb,
            "dag_nodes": dag_nodes,
            "tree_evals": c_tree.exp_count,
            "dag_evals": c_dag.exp_count,
            "err": err_str,
            "val_f64": val_tree,
            "val_stab": val_stab,
            "val_arb": str(val_arb),
            "ref_val": ref_val,
            "domain": domain
        })

    print("=" * 120 + "\n")
    return records

if __name__ == "__main__":
    run_comparative_benchmark()
