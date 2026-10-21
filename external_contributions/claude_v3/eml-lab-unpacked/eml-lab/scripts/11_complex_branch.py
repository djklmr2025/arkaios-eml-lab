"""Experiment: with the PRINCIPAL complex Log, EML reaches i, e^{ix}, cos x, sin x (x real).
Real-only EML cannot (o-minimality, README_v3 §1). Checks: values at high precision, stability across precisions,
and a branch-cut guard (no Log argument may sit on the negative real axis up to rounding)."""
import os, sys, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import mpmath as mp
from eml_lab.core import *
from eml_lab.constructions import Sub19, Add19, L_paper
from eml_lab import complex_constructions as C
from eml_lab.complex_eval import ceval, CDomainError, OnBranchCut

print("== 1. Real blocks fed with COMPLEX inputs (principal Log): the branch cut breaks them ==")
NEG = parse_rpn("11xx1EEE1EEx1E1EE")
blocks = {'Sub19 x-y': (Sub19(X, Y), lambda a, b: a - b), 'Add19 x+y': (Add19(X, Y), lambda a, b: a + b),
          'Neg  -x ': (NEG, lambda a, b: -a), 'L    ln x': (L_paper(X), lambda a, b: mp.log(a))}
random.seed(1); mp.mp.dps = 30
pts = [(mp.mpc(random.uniform(-3, 3), random.uniform(-3, 3)), mp.mpc(random.uniform(-3, 3), random.uniform(-3, 3))) for _ in range(2000)]
for n, (r, t) in blocks.items():
    ok = sum(1 for a, b in pts if abs(ceval(r, {'x': a, 'y': b}, 30) - t(a, b)) < mp.mpf(10) ** -20)
    print(f"  {n}: correct on {ok}/2000 random points of [-3,3]+[-3,3]i")

print("\n== 2. Constants: value and stability at 40, 57, 73, 101, 150, 233, 300 digits ==")
I_ = lambda: mp.mpc(0, 1)
consts = [('i*pi (UNSTABLE route)', C.IPI_UNSTABLE, lambda: I_() * mp.pi), ('1 - i*pi', C.W, lambda: 1 - I_() * mp.pi),
          ('i*pi/2', C.I_HALF_PI, lambda: I_() * mp.pi / 2), ('-i*pi/2', C.MINUS_I_HALF_PI, lambda: -I_() * mp.pi / 2),
          ('i', C.I, I_), ('i*pi', C.IPI, lambda: I_() * mp.pi), ('pi (real!)', C.PI, lambda: mp.pi), ('pi/2', C.HALF_PI, lambda: mp.pi / 2)]
for n, node, t in consts:
    ok = []; cut = False
    for d in (40, 57, 73, 101, 150, 233, 300):
        v = ceval(node, {'x': 0, 'y': 0}, d); mp.mp.dps = d; ok.append(abs(v - t()) < mp.mpf(10) ** -(d - 10))
    try: ceval(node, {'x': 0, 'y': 0}, 80, cut_tol=mp.mpf(10) ** -40)
    except OnBranchCut: cut = True
    print(f"  {n:22s} K={size(node):5d}  correct={sum(ok)}/7  touches_branch_cut={cut}")

print("\n== 3. Functions of a real x, 646 points in [-40,40] (incl. 0, +-1e-12, +-pi, pi/2) ==")
xs = [mp.mpf(k) / 8 for k in range(-320, 321)] + [mp.mpf('1e-12'), mp.mpf('-1e-12'), mp.pi, -mp.pi, mp.pi / 2]
for n, f, t in [('e^{ix}', lambda: C.eix(X), mp.expj), ('e^{-ix}', lambda: C.eix(X, -1), lambda x: mp.expj(-x)),
                ('cos x (v1)', lambda: C.COS(X), mp.cos), ('sin x (v1)', lambda: C.SIN(X), mp.sin),
                ('cos x', lambda: C.COS2(X), mp.cos), ('sin x', lambda: C.SIN2(X), mp.sin)]:
    node = f(); worst = mp.mpf(0); bad = cuts = unstable = 0
    for x in xs:
        dps = 60 + int(abs(x) / 2.3) + 5                     # e^x enters as a phase: ~log10(e^x) extra digits
        try:
            try: ceval(node, {'x': x, 'y': 0}, dps, cut_tol=mp.mpf(10) ** -(dps // 2))
            except OnBranchCut: cuts += 1
            v = ceval(node, {'x': x, 'y': 0}, dps); v2 = ceval(node, {'x': x, 'y': 0}, dps + 37); mp.mp.dps = dps
            unstable += abs(v - v2) > mp.mpf(10) ** -40
            e = abs(v - t(x)); worst = max(worst, e); bad += e > mp.mpf(10) ** -40
        except CDomainError: bad += 1
    print(f"  {n:11s} K={size(node):6,}  unique E={unique_E(node):4d}  depth={depth(node):3d}  "
          f"wrong={bad}  on_cut={cuts}  unstable={unstable}  worst={mp.nstr(worst, 3)}")
print("  on_cut = a Log argument lies on the negative real axis up to rounding; harmless when that Log only enters exp(Log u + c)")
print("  (the 2*pi*i ambiguity cancels) - 'unstable' (result changes with +37 digits) is the test that matters.")
