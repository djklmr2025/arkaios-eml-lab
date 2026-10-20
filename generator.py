"""
EML Expression Generator & DAG Engine
Module 1: Generador de árboles EML y representaciones DAG
"""

import math
from typing import Dict, Any, Set, Tuple, List, Optional

class EMLNode:
    """Nodo inmutable con hash-consing estructural."""
    def __init__(self, key: str, is_op: bool = False, left=None, right=None, val=None):
        self.key = key
        self.is_op = is_op
        self.left = left
        self.right = right
        self.val = val

    def k_tokens(self) -> int:
        """Conteo K en RPN (K = 2*Ops + Leaves)."""
        if not self.is_op:
            return 1
        return 1 + self.left.k_tokens() + self.right.k_tokens()

    def depth(self) -> int:
        if not self.is_op:
            return 0
        return 1 + max(self.left.depth(), self.right.depth())

    def to_rpn(self) -> str:
        if not self.is_op:
            return str(self.val)
        return f"{self.left.to_rpn()} {self.right.to_rpn()} E"

    def collect_dag_nodes(self, visited: Optional[Set[str]] = None) -> Set[str]:
        if visited is None:
            visited = set()
        if self.key not in visited:
            visited.add(self.key)
            if self.is_op:
                self.left.collect_dag_nodes(visited)
                self.right.collect_dag_nodes(visited)
        return visited

    def _eval_op(self, l: float, r: float, counter: Dict[str, int], mode: str = "stabilized") -> float:
        counter["exp"] += 1
        counter["ln"] += 1
        if mode == "stabilized":
            l_clamp = max(-20.0, min(20.0, float(l)))
            r_floor = max(1e-300, float(r))
            return math.exp(l_clamp) - math.log(r_floor)
        # raw float64
        if r <= 0:
            if r == 0:
                ln_r = -float('inf')
            else:
                raise ValueError(f"Domain error: ln({r}) <= 0")
        else:
            ln_r = math.log(r)
        exp_l = 0.0 if l == -float('inf') else math.exp(l)
        return exp_l - ln_r

    def eval_unshared(self, env: Dict[str, float], counter: Dict[str, int], mode: str = "stabilized") -> float:
        """Evaluación pura sobre árbol sin memoización (Representación A)."""
        if not self.is_op:
            if isinstance(self.val, str) and self.val in env:
                return float(env[self.val])
            return float(self.val)
        l = self.left.eval_unshared(env, counter, mode)
        r = self.right.eval_unshared(env, counter, mode)
        return self._eval_op(l, r, counter, mode)

    def eval_memoized(self, env: Dict[str, float], memo: Dict[str, float], counter: Dict[str, int], mode: str = "stabilized") -> float:
        """Evaluación sobre DAG con memoización (Representación B)."""
        if self.key in memo:
            return memo[self.key]
        if not self.is_op:
            res = float(env[self.val]) if (isinstance(self.val, str) and self.val in env) else float(self.val)
            memo[self.key] = res
            return res
        l = self.left.eval_memoized(env, memo, counter, mode)
        r = self.right.eval_memoized(env, memo, counter, mode)
        res = self._eval_op(l, r, counter, mode)
        memo[self.key] = res
        return res

    def __repr__(self):
        if not self.is_op:
            return str(self.val)
        return f"EML[{self.left},{self.right}]"

_CANONICAL_TABLE: Dict[str, EMLNode] = {}

def get_constant(val: float, name: Optional[str] = None) -> EMLNode:
    s = name if name else str(val)
    key = f"Const({s})"
    if key not in _CANONICAL_TABLE:
        _CANONICAL_TABLE[key] = EMLNode(key, is_op=False, val=val)
    return _CANONICAL_TABLE[key]

def get_variable(name: str) -> EMLNode:
    key = f"Var({name})"
    if key not in _CANONICAL_TABLE:
        _CANONICAL_TABLE[key] = EMLNode(key, is_op=False, val=name)
    return _CANONICAL_TABLE[key]

def eml_node(left: EMLNode, right: EMLNode) -> EMLNode:
    key = f"E({left.key},{right.key})"
    if key not in _CANONICAL_TABLE:
        _CANONICAL_TABLE[key] = EMLNode(key, is_op=True, left=left, right=right)
    return _CANONICAL_TABLE[key]

ONE = get_constant(1.0, "1")
