"""
EML Research & Optimization Laboratory (ARKAIOS)
Joint Computational & Mathematical Research with ChatGPT and Copilot.

Core representations:
  A. Raw EML Expression Tree (unshared nodes, full syntactic expansion)
  B. EML Directed Acyclic Graph (DAG) with Common Subexpression Elimination (CSE) & memoized evaluation
  C. Closed-form Algebraic Reference (Ground Truth for domain and numerical precision validation)
"""

import math
import decimal
from decimal import Decimal, getcontext
from typing import Dict, Tuple, Set, Any, List

# 50 decimal places for arbitrary-precision verification
getcontext().prec = 50

class EmlMetrics:
    def __init__(self):
        self.exp_evals = 0
        self.ln_evals = 0

    def reset(self):
        self.exp_evals = 0
        self.ln_evals = 0

class EmlNode:
    """Base class for EML AST/DAG nodes."""
    def __init__(self, key: str):
        self.key = key

    def total_symbols(self) -> int:
        """Total symbols in unshared tree representation."""
        raise NotImplementedError

    def depth(self) -> int:
        """Tree depth."""
        raise NotImplementedError

    def collect_unique_nodes(self, visited: Set[str] = None) -> Set[str]:
        """Unique nodes in DAG representation."""
        raise NotImplementedError

    def eval_tree(self, env: Dict[str, float], metrics: EmlMetrics, mode: str = "float64") -> Any:
        """Evaluation on unshared tree (Representation A)."""
        raise NotImplementedError

    def eval_dag(self, env: Dict[str, float], memo: Dict[str, Any], metrics: EmlMetrics, mode: str = "float64") -> Any:
        """Evaluation on memoized DAG (Representation B)."""
        raise NotImplementedError

class ConstantNode(EmlNode):
    def __init__(self, value: float, name: str = None):
        self.value = value
        self.name = name if name else str(value)
        super().__init__(f"Const({self.name})")

    def total_symbols(self) -> int:
        return 1

    def depth(self) -> int:
        return 0

    def collect_unique_nodes(self, visited: Set[str] = None) -> Set[str]:
        if visited is None:
            visited = set()
        visited.add(self.key)
        return visited

    def eval_tree(self, env: Dict[str, float], metrics: EmlMetrics, mode: str = "float64") -> Any:
        if mode == "arbitrary":
            return Decimal(str(self.value))
        return float(self.value)

    def eval_dag(self, env: Dict[str, float], memo: Dict[str, Any], metrics: EmlMetrics, mode: str = "float64") -> Any:
        return self.eval_tree(env, metrics, mode)

    def __repr__(self):
        return self.name

class VariableNode(EmlNode):
    def __init__(self, name: str):
        self.name = name
        super().__init__(f"Var({name})")

    def total_symbols(self) -> int:
        return 1

    def depth(self) -> int:
        return 0

    def collect_unique_nodes(self, visited: Set[str] = None) -> Set[str]:
        if visited is None:
            visited = set()
        visited.add(self.key)
        return visited

    def eval_tree(self, env: Dict[str, float], metrics: EmlMetrics, mode: str = "float64") -> Any:
        val = env[self.name]
        if mode == "arbitrary":
            return Decimal(str(val))
        return float(val)

    def eval_dag(self, env: Dict[str, float], memo: Dict[str, Any], metrics: EmlMetrics, mode: str = "float64") -> Any:
        return self.eval_tree(env, metrics, mode)

    def __repr__(self):
        return self.name

class EmlOpNode(EmlNode):
    """
    EML Operator node: eml(left, right) = exp(left) - ln(right)
    """
    def __init__(self, left: EmlNode, right: EmlNode):
        self.left = left
        self.right = right
        # Structural hashing for canonical DAG deduplication
        super().__init__(f"eml({left.key}, {right.key})")

    def total_symbols(self) -> int:
        # 1 (eml operator) + left symbols + right symbols
        return 1 + self.left.total_symbols() + self.right.total_symbols()

    def depth(self) -> int:
        return 1 + max(self.left.depth(), self.right.depth())

    def collect_unique_nodes(self, visited: Set[str] = None) -> Set[str]:
        if visited is None:
            visited = set()
        if self.key not in visited:
            visited.add(self.key)
            self.left.collect_unique_nodes(visited)
            self.right.collect_unique_nodes(visited)
        return visited

    def _eval_op(self, l_val: Any, r_val: Any, metrics: EmlMetrics, mode: str) -> Any:
        metrics.exp_evals += 1
        metrics.ln_evals += 1

        if mode == "float64":
            return math.exp(l_val) - math.log(r_val)

        elif mode == "stabilized":
            # Clamping as implemented in WeftOS eml-core stability layer
            # exp input clamped to [-20, 20]
            # ln argument floored to 1e-300
            l_clamped = max(-20.0, min(20.0, float(l_val)))
            r_floored = max(1e-300, float(r_val))
            return math.exp(l_clamped) - math.log(r_floored)

        elif mode == "arbitrary":
            # Python decimal exp and ln
            # Decimal ln requires argument > 0
            dec_l = Decimal(l_val)
            dec_r = Decimal(r_val)
            return dec_l.exp() - dec_r.ln()

        else:
            raise ValueError(f"Unknown mode: {mode}")

    def eval_tree(self, env: Dict[str, float], metrics: EmlMetrics, mode: str = "float64") -> Any:
        l = self.left.eval_tree(env, metrics, mode)
        r = self.right.eval_tree(env, metrics, mode)
        return self._eval_op(l, r, metrics, mode)

    def eval_dag(self, env: Dict[str, float], memo: Dict[str, Any], metrics: EmlMetrics, mode: str = "float64") -> Any:
        if self.key in memo:
            return memo[self.key]
        l = self.left.eval_dag(env, memo, metrics, mode)
        r = self.right.eval_dag(env, memo, metrics, mode)
        val = self._eval_op(l, r, metrics, mode)
        memo[self.key] = val
        return val

    def __repr__(self):
        return f"eml({self.left}, {self.right})"

# ---------------------------------------------------------------------------
# Constructive EML Builders
# ---------------------------------------------------------------------------

ONE = ConstantNode(1.0, "1")

def EML(x: EmlNode, y: EmlNode) -> EmlOpNode:
    return EmlOpNode(x, y)

def eml_exp(x: EmlNode) -> EmlOpNode:
    """exp(x) = eml(x, 1)"""
    return EML(x, ONE)

def eml_ln(x: EmlNode) -> EmlOpNode:
    """ln(x) = eml(1, eml(eml(1, x), 1))  [Odrzywolek 2026 Eq 5]"""
    step1 = EML(ONE, x)
    step2 = EML(step1, ONE)
    return EML(ONE, step2)

def eml_const_e() -> EmlOpNode:
    """e = eml(1, 1)"""
    return EML(ONE, ONE)

def eml_const_zero() -> EmlOpNode:
    """0 = ln(1) = eml(1, eml(eml(1, 1), 1))"""
    return eml_ln(ONE)

def eml_sub(x: EmlNode, y: EmlNode) -> EmlOpNode:
    """
    Subtraction: x - y = eml(ln(x), exp(y))
    Valid for x > 0 and y in R.
    exp(ln(x)) - ln(exp(y)) = x - y.
    """
    return EML(eml_ln(x), eml_exp(y))

def eml_div_log(x: EmlNode, y: EmlNode) -> EmlOpNode:
    """
    Division: x / y = exp(ln(x) - ln(y)) = exp(eml(ln(ln(x)), y))
    = eml(eml(ln(ln(x)), y), 1)
    Valid for x > 1, y > 0.
    """
    ln_x = eml_ln(x)
    ln_ln_x = eml_ln(ln_x)
    diff = EML(ln_ln_x, y)
    return eml_exp(diff)

def eml_div_general(x: EmlNode, y: EmlNode) -> EmlOpNode:
    """
    Division via explicit subtraction:
    x / y = exp(ln(x) - ln(y))
    """
    return eml_exp(eml_sub(eml_ln(x), eml_ln(y)))

def eml_mult_log(x: EmlNode, y: EmlNode) -> EmlOpNode:
    """
    Multiplication for positive reals:
    x * y = exp(ln(x) + ln(y)) = exp(ln(x) - (-ln(y)))
    = exp(ln(x) - (ln(1/y)))
    = exp(eml(ln(ln(x)), div(1, y)))
    """
    inv_y = eml_div_general(ONE, y)
    diff = EML(eml_ln(eml_ln(x)), inv_y)
    return eml_exp(diff)

def eml_sinh(x: EmlNode) -> EmlOpNode:
    """
    Hyperbolic Sine: sinh(x) = (e^x - e^(-x)) / 2
    With e^x - e^(-x) = eml(x, eml(div(1, e^x), 1))
    """
    ex = eml_exp(x)
    inv_ex = eml_div_general(ONE, ex)
    # diff = e^x - e^(-x) = eml(x, exp(inv_ex))
    num = EML(x, eml_exp(inv_ex))
    TWO = ConstantNode(2.0, "2")
    return eml_div_general(num, TWO)

def eml_identity(x: EmlNode) -> EmlOpNode:
    """
    Identity: id(x) = ln(e^x) = eml(1, eml(eml(1, eml(x, 1)), 1))
    Depth 4.
    """
    return eml_ln(eml_exp(x))
