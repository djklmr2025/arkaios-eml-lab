"""Division without an outer multiplication (ARKAIOS-EML, step B).
Idea: x/y = (A - B)/q with q = y^2 > 0, and  T/q = exp(ln T - ln q) = exp( E(ln ln T, q) )  when T > 1.
E(ln ln T, q) = e^{ln ln T} - ln q = ln T - ln q.  Needs T > 1 (so ln ln T is real) and q > 0.
To guarantee A > 1 and B > 1 we can use a decomposition t = F(t) - G(t) with F, G > 1 for every real t:
   F(t) = exp(exp t)      (> 1)          ln F = exp t           (free: no L needed)
   G(t) = exp(exp t) - t  (min ~2.33)    G = E(P(t), P(t))
or the original one (P = e^t, Q = e^t - t >= 1) where A = PxPy + QxQy > 1 always but B can be < 1."""
from .core import *
from .constructions import Sub19, Add19, L_paper, M_opt, M_generic

L = L_paper
def LL(u): return L(L(u))
def divq(T, q):              # T/q  for T > 1, q > 0
    return P(E(LL(T), q))

def AB_PQ(x, y):             # original decomposition (shortcut ln P = t)
    lx, ly = L(Q(x)), L(Q(y))
    A = Add19(P(Add19(x, y)), P(Add19(lx, ly)))
    B = Add19(P(Add19(x, ly)), P(Add19(lx, y)))
    return A, B
def F_(t):  return P(P(t))
def G_(t):  return E(P(t), P(t))
def AB_FG(x, y):             # all four products > 1
    fx, fy = P(x), P(y)                  # ln F
    gx, gy = L(G_(x)), L(G_(y))          # ln G
    A = Add19(P(Add19(fx, fy)), P(Add19(gx, gy)))
    B = Add19(P(Add19(fx, gy)), P(Add19(gx, fy)))
    return A, B

def M_FG(x, y):
    A, B = AB_FG(x, y); return Sub19(A, B)

def V2(x, y, AB=AB_FG, sq=None):
    q = (sq or M_opt)(y, y)
    A, B = AB(x, y)
    return Sub19(divq(A, q), divq(B, q))

# ---- generic search over small design choices ----
def logs(t, kind):           # (ln of positive part, ln of negative part) for t = pos - neg
    if kind == 'PQ': return t, L(Q(t))
    if kind == 'FG': return P(t), L(G_(t))
def add(a, b, flip): return Add19(b, a) if flip else Add19(a, b)
def AB_generic(x, y, kx, ky, flips):
    a1, a2 = logs(x, kx); b1, b2 = logs(y, ky)
    f = iter(flips)
    A = add(P(add(a1, b1, next(f))), P(add(a2, b2, next(f))), next(f))
    B = add(P(add(a1, b2, next(f))), P(add(a2, b1, next(f))), next(f))
    return A, B

# ---- chosen constructions (from the enumeration in scripts/09_division_v2.py) ----
M_FLIPS = (0, 0, 0, 0, 1, 0)
def M571(x, y):
    A, B = AB_generic(x, y, 'PQ', 'PQ', M_FLIPS); return Sub19(A, B)
def V_best(x, y, kx, ky, flips):
    q = M571(y, y); A, B = AB_generic(x, y, kx, ky, flips)
    return Sub19(divq(A, q), divq(B, q))

# ---- variant without the FG tower: keep P/Q, shift B by +1 ----
# A = PxPy + QxQy > 1 always (QxQy >= 1, PxPy > 0); B = PxQy + QxPy > 0 but may be < 1, so use 1 + B > 1.
# x/y = (A - B)/q = A/q - (1+B)/q + 1/q  -> extra term; instead shift both:  (1+A)/q - (1+B)/q.
def one_plus(T): return Add19(ONE, T)          # 1 + T ; ONE is the argument used three times (cheap)
def V_pq(x, y, flips=M_FLIPS, shiftA=True):
    q = M571(y, y); A, B = AB_generic(x, y, 'PQ', 'PQ', flips)
    TA = one_plus(A) if shiftA else A
    return Sub19(divq(TA, q), divq(one_plus(B), q))

# ---- dedicated square: y^2 = (Py - Qy)^2 = [P(2y) + P(2 ly)] - [P(y+ly) + P(y+ly)],  ly = ln Q(y) ----
def SQ(y, o=(0, 0, 0, 0)):
    ly = L(Q(y)); s = Add19(ly, y) if o[0] else Add19(y, ly)
    A = Add19(P(Add19(y, y)), P(Add19(ly, ly))) if not o[1] else Add19(P(Add19(ly, ly)), P(Add19(y, y)))
    B = Add19(P(s), P(s))
    return Sub19(A, B) if not o[2] else Sub19(A, B)
def V_sq(x, y, flips=M_FLIPS, o=(0, 0, 0, 0)):
    q = SQ(y, o); A, B = AB_generic(x, y, 'PQ', 'PQ', flips)
    return Sub19(divq(one_plus(A), q), divq(one_plus(B), q))
