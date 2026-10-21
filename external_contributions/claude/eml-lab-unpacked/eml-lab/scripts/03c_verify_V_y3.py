"""Re-check of V_opt for y=3 (q=y^2=9 needs ~330 digits inside M(y,y); the 60-digit first pass of the adaptive evaluator
produced a spurious ln(0). With the retry-on-DomainError fix these pairs are checked properly."""
import os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import mpmath as mp
from eml_lab.constructions import CATALOG
from eml_lab.evaluators import adaptive_eval, DomainError
root = CATALOG['V_opt'][0]()
for x in [-3, -2, -1, -0.5, 0, 0.5, 1, 2, 3]:
    t0 = time.time()
    try:
        v, d, m = adaptive_eval(root, x, 3, target_digits=30, max_dps=20000)
        mp.mp.dps = d + 10
        print(f"V({x},3) = {mp.nstr(v, 20)}  true={x/3:.17g}  err={mp.nstr(abs(v - mp.mpf(x)/3), 3)}  dps={d}  [{time.time()-t0:.0f}s]", flush=True)
    except (DomainError, RuntimeError) as e:
        print(f"V({x},3) FAIL {e}", flush=True)
