"""Step B: shorter real-global multiplication (K=571) and division (K=2,987) — build, count, export, verify.
Verification: adaptive-precision mpmath with DOMAIN CHECK (every ln argument > 0) on grids, plus SHA-256 export."""
import os, sys, time, json, hashlib, itertools
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import mpmath as mp
from eml_lab.core import *
from eml_lab.constructions import M_opt, V_opt
from eml_lab import division_v2 as d
from eml_lab.evaluators import adaptive_eval2 as adaptive_eval, DomainError, PrecisionTooLow

V_FLIPS = (0, 1, 0, 0, 1, 0)
builds = {
    'M_opt (prev)': lambda: M_opt(X, Y),
    'M571':         lambda: d.M571(X, Y),
    'V_opt (prev)': lambda: V_opt(X, Y),
    'V2959 (FG)':   lambda: d.V_best(X, Y, 'FG', 'PQ', (1, 1, 0, 0, 1, 1)),
    'V2987':        lambda: d.V_pq(X, Y, V_FLIPS),
}
print(f"{'name':13s} {'K':>8s} {'depth':>5s} {'uniqueE':>7s} {'#x':>5s} {'#y':>5s}")
roots = {}
for n, b in builds.items():
    r = b(); roots[n] = r; s = describe(r)
    print(f"{n:13s} {s['K']:>8,} {s['depth']:>5} {s['unique_E']:>7} {s['x_leaves']:>5} {s['y_leaves']:>5}")
os.makedirs('expressions', exist_ok=True)
man = {}
for n in ('M571', 'V2987'):
    txt = rpn(roots[n]); open(f'expressions/{n}.rpn', 'w').write(txt)
    man[n] = dict(describe(roots[n]), sha256_rpn=hashlib.sha256(txt.encode()).hexdigest())
json.dump(man, open('expressions/manifest_v2.json', 'w'), indent=1)
print('exported:', {k: v['sha256_rpn'][:16] for k, v in man.items()})

def check(name, truth, pts, target=30):
    r = roots[name]; worst = mp.mpf(0); bad = 0; mx = 0; t0 = time.time()
    for a, b in pts:
        try: v, used, _ = adaptive_eval(r, a, b, target_digits=target)
        except (DomainError, PrecisionTooLow, RuntimeError) as e: bad += 1; print('  DOMAIN FAIL', name, a, b, e); continue
        mp.mp.dps = used + 10; err = abs(v - truth(mp.mpf(a), mp.mpf(b))) / max(1, abs(truth(mp.mpf(a), mp.mpf(b))))
        worst = max(worst, err); mx = max(mx, used)
    print(f"{name:6s} pairs={len(pts):>3} domain_failures={bad} worst_rel_err={mp.nstr(worst,3):>9s} max_dps={mx:>5} [{time.time()-t0:.1f}s]")
    return bad == 0 and worst < mp.mpf(10) ** -target

mid = [-3, -2, -1, -0.5, 0, 0.5, 1, 2, 3]; nz = [v for v in mid if v != 0]
ok = check('M571', lambda a, b: a * b, list(itertools.product(mid, mid)))
ok &= check('V2987', lambda a, b: a / b, list(itertools.product(mid, nz)))
extra = [(0.5, 0.25), (1.5, 0.1), (-2.75, 0.125), (-2, 4), (4, 4), (3.5, -2.25), (-0.001, 2)]
# NOT in range (documented, not hidden): |y| <= ~0.01 or |y| >= ~6 need > 30,000 digits (see README_v2)
ok &= check('V2987', lambda a, b: a / b, extra)
# V2959 (F=exp(exp t) decomposition) is SHORTER but numerically pathological: show it on two points
for a, b in [(1, 2), (2, 2)]:
    try:
        v, used, m = adaptive_eval(roots['V2959 (FG)'], a, b, max_dps=20000)
        print(f"V2959(FG) at ({a},{b}): needs {used} digits (max log10 exp-arg {m:.0f})")
    except Exception as e: print(f"V2959(FG) at ({a},{b}): infeasible ({type(e).__name__})")
# y = 0 must be a genuine domain failure (division by zero), not a value
try:
    adaptive_eval(roots['V2987'], 1, 0, max_dps=2000); print('y=0: NO FAILURE (unexpected)'); ok = False
except (DomainError, PrecisionTooLow, RuntimeError) as e: print('y=0 correctly rejected:', type(e).__name__)
print('ALL PASSED' if ok else 'SOME CHECK FAILED')
