"""Complex evaluator for EML trees with the PRINCIPAL branch of ln (mpmath: arg in (-pi, pi]).
eml(a,b) = exp(a) - Log(b), b != 0. Same DAGs as the real lab; only the arithmetic changes.
This is the setting in which Odrzywolek claims universality (intermediates may be complex)."""
import mpmath as mp
from .core import G

class CDomainError(ArithmeticError):
    pass

class OnBranchCut(CDomainError):
    pass

def ceval(root, env, dps=50, cut_tol=None):
    """cut_tol: if given, raise OnBranchCut when a Log argument b has Re b < 0 and |Im b| <= cut_tol*|b|
    (its principal value is then decided by rounding noise). An imaginary part that is EXACTLY 0 (the value
    never left the real line, e.g. Log(-1) of the real constant -1) is accepted: arg = pi by convention."""
    mp.mp.dps = dps; nodes = G.nodes; memo = {}
    def f(j):
        if j in memo: return memo[j]
        k, a, b = nodes[j]
        if k == '1': v = mp.mpc(1)
        elif k in env: v = mp.mpc(env[k])
        else:
            bv = f(b)
            if bv == 0: raise CDomainError('Log(0)')
            if cut_tol is not None and bv.real < 0 and 0 < abs(bv.imag) <= cut_tol * abs(bv): raise OnBranchCut(mp.nstr(bv, 10))
            v = mp.exp(f(a)) - mp.log(bv)
        memo[j] = v; return v
    return f(root)
