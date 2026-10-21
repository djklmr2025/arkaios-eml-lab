"""Search for shortest REAL-ONLY EML expressions and verify every candidate in arbitrary precision on a wide grid.
  python scripts/06_search.py --points wide --nmax 12            # reference run
  python scripts/06_search.py --points narrow --nmax 10          # shows why narrow sample points give FALSE 'global' formulas
"""
import os, sys, argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import mpmath as mp
from eml_lab.search import Tables
from eml_lab.core import parse_rpn, size
from eml_lab.evaluators import eval_mp, DomainError
ap = argparse.ArgumentParser(); ap.add_argument('--points', default='wide'); ap.add_argument('--nmax', type=int, default=12)
ap.add_argument('--targets', default='0,-1,2,x-y,x+y,-x,2x,x*y,x/y,1/x,x^2,x/2'); a = ap.parse_args()
print(f"== enumeration, sample points = {a.points} ==")
T = Tables(a.nmax, a.points)
GRID = [-30, -12, -6.3, -3, -1, -0.25, 0.25, 1, 2.7, 3, 6.3, 12, 30]
TRUTH = {'x-y': lambda x, y: x - y, 'x+y': lambda x, y: x + y, '-x': lambda x, y: -x, '2x': lambda x, y: 2 * x, '0': lambda x, y: 0, '-1': lambda x, y: -1,
         '2': lambda x, y: 2, 'x*y': lambda x, y: x * y, 'x/y': lambda x, y: x / y, '1/x': lambda x, y: 1 / x, 'x^2': lambda x, y: x * x, 'x/2': lambda x, y: x / 2}
def verify(rpn_s, truth):
    node = parse_rpn(rpn_s); bad = 0; worst = mp.mpf(0)
    for x in GRID:
        for y in GRID:
            try: v = eval_mp(node, x, y, 400)
            except DomainError: bad += 1; continue
            worst = max(worst, abs(v - truth(mp.mpf(x), mp.mpf(y))))
    return bad, worst
print(f"\n{'target':6s} {'leaves':>6s} {'K':>3s}  {'verification on 169-point grid in [-30,30]^2 (400 digits)':<62s} RPN / note")
for name in a.targets.split(','):
    n, s, how = T.find(name)
    if n is None: print(f"{name:6s} {'-':>6s} {'-':>3s}  {'':<62s} {how}"); continue
    bad, worst = verify(s, TRUTH[name])
    ver = 'GLOBAL OK (0 domain failures, err %s)' % mp.nstr(worst, 2) if bad == 0 and worst < mp.mpf(10) ** -50 else f'NOT GLOBAL: {bad} of 169 grid points leave the real domain'
    print(f"{name:6s} {n:>6} {2*n-1:>3}  {ver:<62s} {s} [{how.split(' ')[0]}]")
