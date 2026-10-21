"""Cheap feasibility probe: evaluate at fixed low precision, abort when an exp ARGUMENT exceeds 10^cap.
Returns max log10|exp argument| (a lower bound of the digits a faithful evaluation needs), or None if > cap.
Values are only indicative at low precision (cancellation), but towers are detected reliably."""
import mpmath as mp
from .core import G
from .evaluators import is_P
class TooBig(Exception): pass
def probe(root, x, y, dps=40, cap=6000):
    mp.mp.dps = dps; nodes = G.nodes; memo = {}; mx = [0.0]
    env = {'x': mp.mpf(x), 'y': mp.mpf(y)}
    def ex(v):
        if v != 0:
            m = float(mp.log10(abs(v)))
            if m > cap: raise TooBig
            mx[0] = max(mx[0], m)
        return mp.exp(v)
    def f(j):
        if j in memo: return memo[j]
        k, a, b = nodes[j]
        if k == '1': v = mp.mpf(1)
        elif k in env: v = env[k]
        elif is_P(b): v = ex(f(a)) - f(nodes[b][1])          # stable rewrite eml(a,exp w)=e^a-w
        else:
            bv = f(b); v = ex(f(a)) - (mp.log(bv) if bv > 0 else mp.mpf('-inf') if bv == 0 else mp.log(abs(bv)))
        memo[j] = v; return v
    try: f(root); return mx[0]
    except TooBig: return None
