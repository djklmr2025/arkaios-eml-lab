"""
ARKAIOS Pi Autosimilarity Module
Verifies π series convergence, the fixed-point autosimilarity S = π + k²·S,
and estimates EML K complexity for π approximation.

Autosimilarity property:
  S = π + k²·S  =>  S·(1 - k²) = π  =>  S* = π / (1 - k²)  for |k| < 1
  The iteration S_{n+1} = π + k²·S_n converges to S* = π/(1-k²).
  This is the geometric series Σ k^(2n)·π = π·1/(1-k²).

K complexity reference:
  EML Add (K=19 via Sub19), EML Division V2987 (K=2987, K_dag=125).
"""

import math
from decimal import Decimal, getcontext
from typing import List, Tuple, Dict

getcontext().prec = 60

PI = math.pi


# ---------------------------------------------------------------------------
# Series Approximations
# ---------------------------------------------------------------------------

def leibniz_pi(n_terms: int) -> float:
    """Leibniz-Gregory series: π/4 = Σ(-1)^k / (2k+1), returns 4·(partial sum)."""
    if n_terms <= 0:
        raise ValueError("n_terms must be >= 1")
    acc = 0.0
    for k in range(n_terms):
        acc += (-1.0) ** k / (2 * k + 1)
    return 4.0 * acc


def nilakantha_pi(n_terms: int) -> float:
    """Nilakantha series: π = 3 + Σ 4·(-1)^(k+1) / (2k·(2k+1)·(2k+2)) for k ≥ 1."""
    if n_terms <= 0:
        raise ValueError("n_terms must be >= 1")
    acc = 3.0
    for k in range(1, n_terms + 1):
        n = 2 * k
        sign = 1.0 if (k % 2 == 1) else -1.0
        acc += sign * 4.0 / (n * (n + 1) * (n + 2))
    return acc


def bbp_pi(n_terms: int) -> float:
    """Bailey–Borwein–Plouffe: π = Σ 1/16^k·[4/(8k+1) - 2/(8k+4) - 1/(8k+5) - 1/(8k+6)]."""
    if n_terms <= 0:
        raise ValueError("n_terms must be >= 1")
    acc = 0.0
    for k in range(n_terms):
        factor = 1.0 / (16 ** k)
        acc += factor * (
            4.0 / (8 * k + 1)
            - 2.0 / (8 * k + 4)
            - 1.0 / (8 * k + 5)
            - 1.0 / (8 * k + 6)
        )
    return acc


# ---------------------------------------------------------------------------
# Autosimilarity Fixed-Point Verification
# ---------------------------------------------------------------------------

def autosimilar_fixed_point(
    k: float,
    n_iter: int = 500,
    tol: float = 1e-15,
) -> Tuple[float, bool, float]:
    """
    Iterates S_{n+1} = π + k²·S_n from S_0 = 0.

    Args:
        k: parameter with |k| < 1 for convergence.
        n_iter: maximum iterations.
        tol: early-stop tolerance on |S_{n+1} - S_n|.

    Returns:
        (S_converged, converged_flag, expected_limit)
        where expected_limit = π / (1 - k²).
    """
    if abs(k) >= 1.0:
        raise ValueError(f"Fixed-point diverges: |k| = {abs(k):.6f} >= 1")
    k_sq = k * k
    S = 0.0
    for _ in range(n_iter):
        S_new = PI + k_sq * S
        if abs(S_new - S) < tol:
            S = S_new
            break
        S = S_new
    expected = PI / (1.0 - k_sq)
    converged = abs(S - expected) < 1e-10
    return S, converged, expected


def verify_autosimilarity(
    k_values: List[float],
    n_iter: int = 500,
) -> List[Dict]:
    """
    For each k in k_values, verifies the fixed-point S = π/(1-k²).

    Returns list of dicts with keys: k, S, expected, abs_error, converged.
    """
    results = []
    for k in k_values:
        try:
            S, converged, expected = autosimilar_fixed_point(k, n_iter)
            results.append({
                "k": k,
                "S": S,
                "expected": expected,
                "abs_error": abs(S - expected),
                "converged": converged,
            })
        except ValueError as exc:
            results.append({"k": k, "abs_error": None, "converged": False, "error_msg": str(exc)})
    return results


# ---------------------------------------------------------------------------
# K Complexity Estimation
# ---------------------------------------------------------------------------

def eml_k_complexity_pi(
    n_terms: int,
    k_add: int = 19,
    k_div: int = 2987,
    constant_folding: bool = False,
) -> int:
    """
    Estimates K complexity (EML tree token count) to express π via Leibniz series
    with n_terms terms.

    Args:
        n_terms: number of series terms.
        k_add: K complexity of EML addition (default 19, Sub19/Add19 basis).
        k_div: K complexity of EML division (default 2987, V2987 basis).
        constant_folding: if True, rational terms are precomputed constants (K=1 each).

    Returns:
        Total estimated K token count.
    """
    if n_terms <= 0:
        raise ValueError("n_terms must be >= 1")
    k_per_term = 1 if constant_folding else k_div
    k_terms = n_terms * k_per_term
    k_additions = max(0, n_terms - 1) * k_add
    return k_terms + k_additions


def k_complexity_table(
    n_terms_list: List[int],
    k_add: int = 19,
    k_div: int = 2987,
) -> List[Dict]:
    """Returns K complexity for each n in n_terms_list, with and without constant folding."""
    rows = []
    for n in n_terms_list:
        rows.append({
            "n_terms": n,
            "K_symbolic": eml_k_complexity_pi(n, k_add=k_add, k_div=k_div, constant_folding=False),
            "K_folded": eml_k_complexity_pi(n, k_add=k_add, k_div=k_div, constant_folding=True),
        })
    return rows


# ---------------------------------------------------------------------------
# Convergence Table
# ---------------------------------------------------------------------------

def verify_convergence_table(
    n_terms_list: List[int],
    series: str = "leibniz",
) -> List[Tuple[int, float, float, int]]:
    """
    Returns (n, approx, abs_error, K_complexity) for each n in n_terms_list.

    Args:
        n_terms_list: list of term counts to evaluate.
        series: 'leibniz', 'nilakantha', or 'bbp'.

    Returns:
        List of tuples (n, approx, abs_error, K_complexity).
    """
    series_fns = {"leibniz": leibniz_pi, "nilakantha": nilakantha_pi, "bbp": bbp_pi}
    if series not in series_fns:
        raise ValueError(f"Unknown series '{series}'. Choose from: {list(series_fns)}")
    fn = series_fns[series]
    rows = []
    for n in n_terms_list:
        approx = fn(n)
        error = abs(approx - PI)
        k = eml_k_complexity_pi(n)
        rows.append((n, approx, error, k))
    return rows


if __name__ == "__main__":
    print("=== ARKAIOS Pi Autosimilarity Module ===\n")

    print("-- Convergence Table (Leibniz series) --")
    table = verify_convergence_table([10, 100, 1000, 10000], series="leibniz")
    for n, approx, err, k in table:
        print(f"  n={n:6d}: pi ~ {approx:.10f}  |error| = {err:.2e}  K_complexity = {k}")

    print("\n-- BBP Series --")
    for n in [5, 10, 15]:
        val = bbp_pi(n)
        print(f"  bbp({n:2d} terms): {val:.15f}  |error| = {abs(val - PI):.2e}")

    print("\n-- Autosimilarity Fixed-Point Verification --")
    results = verify_autosimilarity([0.1, 0.3, 0.5, 0.7, 0.9])
    for r in results:
        print(
            f"  k={r['k']:.1f}: S = {r['S']:.10f}, expected = {r['expected']:.10f}, "
            f"error = {r['abs_error']:.2e}, converged = {r['converged']}"
        )

    print("\n-- K Complexity Table --")
    for row in k_complexity_table([10, 100, 1000]):
        print(
            f"  n={row['n_terms']:5d}: K_symbolic={row['K_symbolic']:8d}, K_folded={row['K_folded']:5d}"
        )
