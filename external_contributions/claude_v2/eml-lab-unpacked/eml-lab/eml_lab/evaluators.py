"""Evaluators. Three EXECUTION strategies and two ARITHMETICS, reported separately.

strategy:
  'tree'        pure EML tree evaluation: every occurrence recomputed (exp calls = ln calls = (K-1)/2)
  'dag'         memoised per unique node (exp/ln calls = unique_E)
  'dag_stable'  'dag' + exact real peephole  eml(a, exp(w)) = exp(a) - w   (no ln, no exp(w) needed).
                This rewrite is valid for ALL real w (exp(w) > 0 so the left side is always defined),
                therefore it does not change the domain; it only avoids overflow/underflow of exp(w).
arith:
  'f64'  numpy float64 (silent nan/inf)      'mp'  mpmath at the current mp.mp.dps, with DOMAIN CHECK
"""
import time
import numpy as np
import mpmath as mp
from .core import G

class DomainError(ArithmeticError):
    pass

class Stats:
    def __init__(self): self.exp_calls = 0; self.ln_calls = 0; self.node_evals = 0; self.max_log10 = 0.0; self.seconds = 0.0
    def as_dict(self): return dict(exp_calls=self.exp_calls, ln_calls=self.ln_calls, node_evals=self.node_evals,
                                   max_log10=round(self.max_log10, 3), seconds=round(self.seconds, 4))

def is_P(j):
    """node j is exp(w) = E(w, 1)"""
    k, a, b = G.nodes[j]
    return k == 'E' and G.nodes[b][0] == '1'

def evaluate(root, env, arith='f64', strategy='dag', stats=None):
    """env: {'x': value, 'y': value}. Returns the value. With arith='mp' raises DomainError if some ln argument <= 0."""
    st = stats or Stats()
    nodes = G.nodes
    memo = {}
    track = (arith == 'mp')
    if arith == 'f64':
        one = np.float64(1.0); xp = np.exp; lg = np.log
    else:
        one = mp.mpf(1)
        xp = mp.exp
        def lg(v):
            if not v > 0: raise DomainError('ln argument <= 0: %s' % mp.nstr(v, 8))
            return mp.log(v)
    def note(v):
        if track and v != 0:
            m = float(mp.log10(abs(v)));
            if m > st.max_log10: st.max_log10 = m
    def f(j):
        if strategy != 'tree' and j in memo: return memo[j]
        k, a, b = nodes[j]
        if k == '1': v = one
        elif k == 'x' or k == 'y': v = env[k]
        else:
            st.node_evals += 1
            if strategy == 'dag_stable' and is_P(b):
                w = f(nodes[b][1]); av = f(a); note(av); ea = xp(av); st.exp_calls += 1; v = ea - w
            else:
                av = f(a); note(av); ea = xp(av); st.exp_calls += 1
                lb = lg(f(b)); st.ln_calls += 1
                v = ea - lb
        if strategy != 'tree': memo[j] = v
        return v
    t0 = time.perf_counter()
    with np.errstate(all='ignore'):
        out = f(root)
    st.seconds = time.perf_counter() - t0
    return out

def eval_mp(root, x, y, dps, strategy='dag', stats=None):
    """Evaluate at `dps` digits; x, y are floats (converted exactly) or mpf."""
    mp.mp.dps = dps
    return evaluate(root, {'x': mp.mpf(x), 'y': mp.mpf(y)}, 'mp', strategy, stats)

def eval_f64(root, x, y, strategy='dag', stats=None):
    return evaluate(root, {'x': np.float64(x), 'y': np.float64(y)}, 'f64', strategy, stats)

def adaptive_eval(root, x, y, target_digits=30, guard=30, start_dps=60, max_dps=60000):
    """Heuristic adaptive-precision evaluation (NOT a rigorous interval method).
    Rule of thumb: an exp argument v of magnitude 10^m has absolute precision 10^(m-dps), and the cancellation
    ln(exp(v)) = v therefore costs m digits. (Only EXP ARGUMENTS are tracked: nodes of the form exp(v) can be astronomically
    large, e.g. 10^(10^295), but they are only ever logged again.) So: evaluate, read the largest log10|exp argument|,
    raise dps to  m + target + guard, re-evaluate, and confirm with a second run at +60 digits.
    Returns (value, dps_used, max_log10). Raises DomainError if some ln argument <= 0."""
    d = start_dps
    while d <= max_dps:
        st = Stats()
        try:
            v = eval_mp(root, x, y, d, 'dag', st)
        except DomainError:
            # At too low a precision cancellation can produce a spurious 0 or negative ln argument.
            # Retry with more digits; a GENUINE domain failure would persist up to max_dps and is re-raised.
            if 2 * d > max_dps: raise
            d *= 2; continue
        need = int(st.max_log10) + target_digits + guard
        if need > max_dps: raise RuntimeError('needs about %d digits (> max_dps=%d)' % (need, max_dps))
        if d >= need:
            v2 = eval_mp(root, x, y, d + 60, 'dag')
            tol = mp.mpf(10) ** (-target_digits) * max(1, abs(v2))
            if abs(v - v2) <= tol: return v2, d + 60, st.max_log10
            need = d * 2
        d = max(need, d + 1)
    raise RuntimeError('max_dps exceeded')

class PrecisionTooLow(ArithmeticError):
    pass

def eval_mp_capped(root, x, y, dps, stats=None):
    """Like eval_mp(strategy='dag') but raises PrecisionTooLow as soon as an exp ARGUMENT reaches 10^(dps-10):
    at that point the argument has no correct digit left after the decimal point, so the result cannot be trusted
    anyway, and computing exp of it may be astronomically expensive (exp of a garbage 10^50 -> tower)."""
    st = stats or Stats(); mp.mp.dps = dps; nodes = G.nodes; memo = {}
    env = {'x': mp.mpf(x), 'y': mp.mpf(y)}; lim = dps - 10
    def f(j):
        if j in memo: return memo[j]
        k, a, b = nodes[j]
        if k == '1': v = mp.mpf(1)
        elif k in env: v = env[k]
        else:
            av = f(a)
            if av != 0:
                m = float(mp.log10(abs(av)))
                if m > lim: raise PrecisionTooLow(m)
                st.max_log10 = max(st.max_log10, m)
            bv = f(b)
            if not bv > 0: raise DomainError('ln argument <= 0: %s' % mp.nstr(bv, 8))
            v = mp.exp(av) - mp.log(bv); st.exp_calls += 1; st.ln_calls += 1
        memo[j] = v; return v
    return f(root)

def adaptive_eval2(root, x, y, target_digits=30, guard=30, start_dps=60, max_dps=60000):
    """adaptive_eval with the cap above. Spurious domain errors / too-large exp arguments at low precision
    trigger a retry with twice the digits; a failure that persists up to max_dps is re-raised (still heuristic)."""
    d = start_dps
    while True:
        st = Stats()
        try:
            v = eval_mp_capped(root, x, y, d, st)
        except (DomainError, PrecisionTooLow):
            if 2 * d > max_dps: raise
            d *= 2; continue
        need = int(st.max_log10) + target_digits + guard
        if d >= need:
            try: v2 = eval_mp_capped(root, x, y, d + 60)
            except (DomainError, PrecisionTooLow):
                d *= 2; continue
            mp.mp.dps = d + 60
            if abs(v - v2) <= mp.mpf(10) ** (-target_digits) * max(1, abs(v2)): return v2, d + 60, st.max_log10
            need = 2 * d
        if need > max_dps: raise RuntimeError('needs about %d digits (> max_dps=%d)' % (need, max_dps))
        d = max(need, d + 1)
