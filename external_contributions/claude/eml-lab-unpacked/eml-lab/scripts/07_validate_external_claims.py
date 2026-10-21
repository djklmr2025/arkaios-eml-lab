"""Checks of claims made in two external documents (Antigravity report, Copilot summary). Independent of the main package logic
except for the RPN parser/DAG sizes. Each line prints CLAIM -> RESULT."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import mpmath as mp
from eml_lab.core import parse_rpn, size, X, Y, ONE, Z, E, P
from eml_lab.constructions import L_paper, L_Z
from eml_lab.evaluators import eval_mp, DomainError
mp.mp.dps = 60
def ev(node, x, y=1):
    try: return eval_mp(node, x, y, 60)
    except DomainError as e: return 'DOMAIN FAIL (%s)' % e
def zz(name): return Z   # constant 0 as a K=7 subtree
print("--- Antigravity: 'L(x) = eml(0, eml(x,1)) = ln(x)' ---")
Lbad = E(Z, E(X, ONE))
for x in (2, 5): print(f"  L_claim({x}) = {mp.nstr(ev(Lbad, x), 10)}   ln({x}) = {mp.nstr(mp.log(x), 10)}   (it equals 1-x = {1-x})")
print("--- Antigravity: 'Neg(z) = eml(0, eml(0, eml(z,1))) = -z' ---")
Nbad = E(Z, E(Z, E(X, ONE)))
for x in (0.5, 2): print(f"  Neg_claim({x}) = {mp.nstr(ev(Nbad, x), 10)}   -x = {-x}   (it equals 1 - ln(1-x), defined only for x<1)" if x < 1 else f"  Neg_claim({x}) = {ev(Nbad, x)}   -x = {-x}")
print("--- Antigravity: 'V(x,y)=exp(eml(ln(ln x), y)) , K=17, domain x>1, y>0' ---")
lnln = L_paper(L_paper(X))                         # ln(ln x)
Vc = P(E(lnln, Y))
print("  K =", size(Vc))
worst = 0
for x in (1.5, 2, 10, 100):
    for y in (0.1, 1, 3, 7.5):
        v = ev(Vc, x, y); worst = max(worst, abs(v - mp.mpf(x) / mp.mpf(y)))
print("  max |err| over x in {1.5,2,10,100}, y in {0.1,1,3,7.5}: ", mp.nstr(worst, 3))
for x, y in [(1, 2), (0.5, 2), (-3, 2), (2, -1), (0, 1)]: print(f"  outside domain: V({x},{y}) ->", ev(Vc, x, y) if not isinstance(ev(Vc, x, y), mp.mpf) else mp.nstr(ev(Vc, x, y), 8))
print("--- 'Sub K=11' : D(x,y)=eml(ln x, exp y) with the paper's ln ---")
Dn = E(L_paper(X), P(Y)); print("  K =", size(Dn))
for x, y in [(3, 1), (5, -2), (0.5, 4), (0, 1), (-2, 1)]:
    r = ev(Dn, x, y); print(f"  D({x},{y}) = {mp.nstr(r, 8) if isinstance(r, mp.mpf) else r}   x-y = {x-y}")
print("--- Copilot open question: constants -1 and 2 with only E and 1 (found by search; verified here) ---")
for name, s, val in [('-1', '11111EEE1EE11E1EE', -1), ('2', '111111EEE1EE11EE1EE', 2), ('0 (Z)', '111E1EE', 0)]:
    node = parse_rpn(s); r = ev(node, 0)
    print(f"  {name}: RPN {s}  K={size(node)}  value={mp.nstr(r, 15) if isinstance(r, mp.mpf) else r}")
print("--- Copilot: reflection C(x)=1-x and R_a(x)=exp(a)-x and translation T_{a,b}(x)=x+exp(a)-exp(b) ---")
a, b = mp.mpf('0.7'), mp.mpf('-1.3')
R = lambda aa, t: mp.e**aa - t
print("  R_a(x) numeric identity, x=-4.2:", mp.nstr(mp.e**a - mp.log(mp.e**mp.mpf('-4.2')), 12), "vs", mp.nstr(R(a, mp.mpf('-4.2')), 12))
print("  T_{a,b}(x) numeric identity, x=2.5:", mp.nstr(R(a, R(b, mp.mpf('2.5'))), 12), "vs", mp.nstr(mp.mpf('2.5') + mp.e**a - mp.e**b, 12))
