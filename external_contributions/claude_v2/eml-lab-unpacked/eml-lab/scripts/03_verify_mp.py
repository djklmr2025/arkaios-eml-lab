"""Arbitrary-precision verification of algebraic equivalence AND real domain (every ln argument > 0).
Priority A: V_opt (K=88,715) is verified here with the adaptive-precision evaluator."""
import os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import mpmath as mp
from eml_lab.constructions import CATALOG
from eml_lab.evaluators import eval_mp, adaptive_eval, DomainError, Stats

def check(name, xs, ys, dps=None, target=30):
    build, truth = CATALOG[name]; root = build()
    worst = mp.mpf(0); bad = 0; maxdps = 0; t0 = time.time(); n = 0
    for a in xs:
        for b in ys:
            n += 1
            try:
                if dps: v = eval_mp(root, a, b, dps); used = dps
                else:   v, used, _ = adaptive_eval(root, a, b, target_digits=target)
            except DomainError as e:
                bad += 1; print('   DOMAIN FAIL', name, a, b, e); continue
            mp.mp.dps = max(used, 60) + 10
            err = abs(v - truth(mp.mpf(a), mp.mpf(b)))
            worst = max(worst, err); maxdps = max(maxdps, used)
    print(f"{name:9s} pairs={n:>3}  domain_failures={bad}  worst_abs_err={mp.nstr(worst, 3):>10s}  max_dps_used={maxdps:>5}  [{time.time()-t0:.1f}s]")
    return bad == 0 and worst < mp.mpf(10) ** (-target)

wide = [-30, -12, -6.3, -3, -1, -0.25, 0, 0.25, 1, 2.7, 3, 6.3, 12, 30]
mid = [-3, -2, -1, -0.5, 0, 0.5, 1, 2, 3]
nz = [-3, -2, -1, -0.5, 0.5, 1, 2, 3]
ok = True
print("== Sub / Add, 196 pairs in [-30,30]^2, fixed 400 digits ==")
for nm in ('Sub_orig', 'Add_orig', 'Sub_pl', 'Sub19', 'Add19'): ok &= check(nm, wide, wide, dps=400)
print("== Products, 81 pairs in [-3,3]^2, adaptive precision (target 30 digits) ==")
for nm in ('M_orig', 'M_pl', 'M_opt'): ok &= check(nm, mid, mid)
xs_v = [-2, -1, -0.5, 0, 0.5, 1, 2]; ys_v = [-2, -1, -0.5, 0.5, 1, 2]
if os.environ.get('FULL_V'):            # |x*y| up to 9 needs thousands of digits: slow, optional
    xs_v, ys_v = mid, nz
print("== Division V_opt (K=88,715), x in %s, y in %s, adaptive precision (priority A) ==" % (xs_v, ys_v))
ok &= check('V_opt', xs_v, ys_v)
print("ALL PASSED" if ok else "SOME CHECK FAILED")
sys.exit(0 if ok else 1)
