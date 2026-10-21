"""Experimental: i, e^{ix}, cos x, sin x as EML trees evaluated with the principal complex Log.
Strategy: never ask a block to add/subtract numbers whose imaginary part is large; put the imaginary
'rotation' inside exp and let exp(Log u + Log v) = u*v absorb the 2*pi*i ambiguity of Log."""
from .core import *
from .constructions import Sub19, Add19, L_paper as L

NEG1 = parse_rpn("11111EEE1EE11E1EE")            # -1   (real, K=17)
TWO = parse_rpn("111111EEE1EE11EE1EE")           # 2    (real, K=19)
LN2 = L(TWO)                                     # ln 2
def Mc(u, v): return P(Add19(L(u), L(v)))       # u*v for u,v != 0   (exp removes the 2*pi*i ambiguity)
def half(w):  return P(Sub19(L(w), LN2))        # w/2 for w != 0
# i = exp(i*pi/2):   Log(-1) = i*pi  ->  i*pi/2 = half(i*pi)  ->  i = exp(i*pi/2)
# UNSTABLE (kept as a counterexample): Sub19 evaluates Log of a value that is EXACTLY -e, i.e. ON the branch cut;
# rounding noise decides +i*pi or -i*pi (wrong at 73, 101, 150 digits). Do not use.
IPI_UNSTABLE = Sub19(ONE, E(Z, NEG1))
# Stable route: W = E(0,-1) = 1 - Log(-1) = 1 - i*pi (Log(-1) of an exactly real -1 is well defined),
# then halve W (W is far from the cut) and remove the real part 1/2.
W = E(Z, NEG1)                                   # 1 - i*pi
HALF = half(ONE)                                 # 1/2
WH = half(W)                                     # 1/2 - i*pi/2
I_HALF_PI = Sub19(HALF, WH)                      #  i*pi/2
MINUS_I_HALF_PI = Sub19(WH, HALF)                # -i*pi/2
I = P(I_HALF_PI)                                 # i
IPI = Add19(I_HALF_PI, I_HALF_PI)                # i*pi (for reference only)
def eix(x, sign=+1):
    """e^{+-ix} for real x, via x = Px - Qx (Px = e^x > 0, Qx = e^x - x >= 1):
       e^{ix} = e^{i Px} * e^{-i Qx};  i*Px = exp(i pi/2 + x),  i*Qx = exp(i pi/2 + ln Qx)."""
    ip, im = (I_HALF_PI, MINUS_I_HALF_PI) if sign > 0 else (MINUS_I_HALF_PI, I_HALF_PI)
    a = P(P(Add19(ip, x)))                       # e^{ i Px}  (sign>0)
    b = P(P(Add19(im, L(Q(x)))))                 # e^{-i Qx}
    return Mc(a, b)
def COS(x): return half(Add19(eix(x, +1), eix(x, -1)))
def SIN(x):  # sin x = (e^{ix} - e^{-ix}) / (2i) = half( (e^{ix}-e^{-ix}) * (-i) )
    return half(Mc(Sub19(eix(x, +1), eix(x, -1)), P(MINUS_I_HALF_PI)))

# ---- zero-safe versions (the ones above hit Log(0) where the value is exactly 0: sin at x=0, ...) ----
THREE = Add19(TWO, ONE)                          # 3
THREE_HALVES = half(THREE)                       # 3/2
PI = Mc(IPI, P(MINUS_I_HALF_PI))                 # (i*pi)*(-i) = pi   (a REAL constant reached through C)
HALF_PI = Mc(I_HALF_PI, P(MINUS_I_HALF_PI))      # pi/2
def COS2(x):
    """cos x = (2 cos x + 3)/2 - 3/2 ; the Log argument 2cos x + 3 is >= 1, never 0."""
    return Sub19(half(Add19(THREE, Add19(eix(x, +1), eix(x, -1)))), THREE_HALVES)
def SIN2(x):
    """sin x = cos(x - pi/2)"""
    return COS2(Sub19(x, HALF_PI))
