"""Every construction discussed in the ARKAIOS-EML review, as functions building DAG nodes.
All formulas are over the REAL numbers: every ln argument is positive for every real input
(argument in README; checked numerically by scripts/03_verify_mp.py)."""
from .core import *

# (1) ORIGINAL proposal (Z-based ln, subtraction via the shift R_y(t) = exp(y) - t)
def L_Z(u):      return E(Z, E(E(Z, u), ONE))              # ln u, u>0
def Sub_orig(x, y):
    R = lambda t: E(y, P(t))                               # R_y(t) = e^y - t
    return E(L_Z(R(y)), P(R(x)))                           # D(R_y(y), R_y(x)) = x - y
def Neg_orig(a):     return Sub_orig(Z, a)
def Add_orig(a, b):  return Sub_orig(a, Neg_orig(b))
def Mpos_orig(u, v): return P(Add_orig(L_Z(u), L_Z(v)))    # u*v for u,v>0
def M_orig(x, y):
    A = Add_orig(Mpos_orig(P(x), P(y)), Mpos_orig(Q(x), Q(y)))
    B = Add_orig(Mpos_orig(P(x), Q(y)), Mpos_orig(Q(x), P(y)))
    return Sub_orig(A, B)                                  # (Px-Qx)(Py-Qy) = x*y
def V_orig(x, y):
    q = M_orig(y, y)                                       # y^2 > 0
    r = P(Sub_orig(L_Z(ONE), L_Z(q)))                      # 1/y^2   (as proposed, with L(1))
    return M_orig(M_orig(x, y), r)                         # x*y*(1/y^2) = x/y

# (2) Intermediate: ln from eq. (5) of Odrzywolek (uses the constant 1 instead of Z)
def L_paper(u):  return E(ONE, E(E(ONE, u), ONE))          # ln u, u>0
def Sub_pl(x, y):
    R = lambda t: E(y, P(t))
    return E(L_paper(R(y)), P(R(x)))
def Add_pl(a, b):    return Sub_pl(a, Sub_pl(Z, b))
def M_generic(x, y, Sub, Add, L, shortcut=True):
    """x*y = (Px-Qx)(Py-Qy) with Px=e^x, Qx=e^x-x (both >0).
    shortcut=True uses ln(P(t)) = t, so only L(Q(.)) is needed."""
    Px, Py, Qx, Qy = P(x), P(y), Q(x), Q(y)
    if shortcut:
        lx, ly = L(Qx), L(Qy)
        A = Add(P(Add(x, y)), P(Add(lx, ly)))              # PxPy + QxQy
        B = Add(P(Add(x, ly)), P(Add(lx, y)))              # PxQy + QxPy
    else:
        Mp = lambda u, v: P(Add(L(u), L(v)))
        A = Add(Mp(Px, Py), Mp(Qx, Qy)); B = Add(Mp(Px, Qy), Mp(Qx, Py))
    return Sub(A, B)
def M_pl(x, y):  return M_generic(x, y, Sub_pl, Add_pl, L_paper, shortcut=False)

# (3) Optimised: K=19 subtraction / addition found by scripts/06_search.py (real-only, global)
SUB_RPN = "11yy1EEE1EEyx1EE1EE"    # as a function of (x,y): x - y     (y appears 3 times)
ADD_RPN = "x11xx1EEE1EEy1EE1EE"    # as a function of (x,y): x + y     (x appears 3 times)
def Sub19(a, b): return parse_rpn(SUB_RPN, {'x': a, 'y': b})
def Add19(a, b): return parse_rpn(ADD_RPN, {'x': a, 'y': b})
def M_opt(x, y): return M_generic(x, y, Sub19, Add19, L_paper, shortcut=True)
def V_opt(x, y):
    """x / y for y != 0 :  M(M(x,y), 1/y^2),  with 1/y^2 = exp(0 - ln(y^2))."""
    q = M_opt(y, y)
    r = P(Sub19(Z, L_paper(q)))
    return M_opt(M_opt(x, y), r)

CATALOG = {   # name -> (builder of the node over leaves x,y ; true function)
    'Sub_orig': (lambda: Sub_orig(X, Y), lambda a, b: a - b),
    'Add_orig': (lambda: Add_orig(X, Y), lambda a, b: a + b),
    'M_orig':   (lambda: M_orig(X, Y),   lambda a, b: a * b),
    'V_orig':   (lambda: V_orig(X, Y),   lambda a, b: a / b),
    'Sub_pl':   (lambda: Sub_pl(X, Y),   lambda a, b: a - b),
    'Add_pl':   (lambda: Add_pl(X, Y),   lambda a, b: a + b),
    'M_pl':     (lambda: M_pl(X, Y),     lambda a, b: a * b),
    'Sub19':    (lambda: Sub19(X, Y),    lambda a, b: a - b),
    'Add19':    (lambda: Add19(X, Y),    lambda a, b: a + b),
    'M_opt':    (lambda: M_opt(X, Y),    lambda a, b: a * b),
    'V_opt':    (lambda: V_opt(X, Y),    lambda a, b: a / b),
}
