"""float64 benchmark: plain vs stable (peephole) evaluation, failure catalogue, and the M(3,3) case study."""
import os, sys, csv
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np, mpmath as mp
from eml_lab.constructions import M_opt, V_opt, Sub19, Add19
from eml_lab.core import X, Y
from eml_lab.evaluators import eval_f64, eval_mp, adaptive_eval, Stats

def score(root, truth, pts, strategy, tol=1e-6):
    ok = 0
    for a, b in pts:
        v = eval_f64(root, a, b, strategy)
        if np.isfinite(v) and abs(v - truth(a, b)) <= tol * max(1.0, abs(truth(a, b))): ok += 1
    return ok

g = np.arange(-8, 8.01, 0.25); grid = [(a, b) for a in g for b in g]
M, V, S, A = M_opt(X, Y), V_opt(X, Y), Sub19(X, Y), Add19(X, Y)
print("== correctness of float64 results (tolerance 1e-6 relative to max(1,|true|)), grid [-8,8]^2 step 0.25 (4225 pts) ==")
for nm, root, tr in [('Sub19', S, lambda a, b: a - b), ('Add19', A, lambda a, b: a + b), ('M_opt', M, lambda a, b: a * b)]:
    print(f"{nm:6s} dag: {score(root, tr, grid, 'dag'):>5}   dag_stable: {score(root, tr, grid, 'dag_stable'):>5}   (of {len(grid)})")
nzgrid = [(a, b) for a, b in grid if b != 0]
print(f"V_opt  dag: {score(V, lambda a, b: a / b, nzgrid, 'dag'):>5}   dag_stable: {score(V, lambda a, b: a / b, nzgrid, 'dag_stable'):>5}   (of {len(nzgrid)})")
for tol in (1e-9, 1e-12):
    print(f"M_opt dag_stable at tol {tol:g}: {score(M, lambda a, b: a * b, grid, 'dag_stable', tol)}")

print("\n== failure catalogue for M_opt (also written to results/failures_M.csv) ==")
rows = []
for a, b in [(1, 1), (2, 2), (3, 3), (5, 5), (-8, -8), (-6, 2), (3, -3), (7, -7), (8, 8), (10, 10), (0.5, 0.5), (1.5, 1.5), (-3, -3), (2, 3)]:
    p = eval_f64(M, a, b, 'dag'); s = eval_f64(M, a, b, 'dag_stable'); t = a * b
    mp.mp.dps = 5; adaptive = ''
    if max(abs(a), abs(b)) > 4:
        adaptive = 'skipped: needs > 3000 digits (observed for (5,5); cost grows double-exponentially)'
        rows.append((a, b, t, float(p), float(s), adaptive)); print(f"M({a},{b}): true={t}  plain={p}  stable={s}  adaptive_mp={adaptive}"); continue
    try:
        v, d, m = adaptive_eval(M, a, b, target_digits=20, max_dps=3000)
        adaptive = f"{mp.nstr(v, 12)} (dps={d})"
    except Exception as e: adaptive = 'needs > 3000 digits (cap of this benchmark)'
    rows.append((a, b, t, float(p), float(s), adaptive))
    print(f"M({a},{b}): true={t}  plain={p}  stable={s}  adaptive_mp={adaptive}")
with open(os.path.join(os.path.dirname(__file__), '..', 'results', 'failures_M.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['x', 'y', 'true', 'float64_plain', 'float64_stable', 'adaptive_mp']); w.writerows(rows)

print("\n== M(3,3) case study: result vs working precision (the double-exponential cancellation) ==")
for d in (50, 100, 200, 250, 290, 300, 320, 360, 420, 600):
    st = Stats(); v = eval_mp(M, 3, 3, d, 'dag', st)
    print(f"dps={d:>4}  M(3,3)={mp.nstr(v, 12):>14s}  largest exp-argument ~ 10^{st.max_log10:.1f}")
print("Rule observed: digits needed ~ log10(largest exp argument) + target. At (3,3) that is ~10^298 -> ~330+ digits.")
print("float64 has 16 digits and cannot even represent exp(10^298); the stable rewrite removes overflow but not cancellation.")
