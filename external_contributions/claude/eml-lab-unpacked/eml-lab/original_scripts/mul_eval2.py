import sys, mpmath as mp, numpy as np, warnings
warnings.filterwarnings('ignore')
sys.setrecursionlimit(100000)
# ---- hash-consed DAG ----
nodes=[]; table={}
def mk(kind,a=None,b=None):
    key=(kind,a,b)
    if key in table: return table[key]
    nodes.append(key); table[key]=len(nodes)-1; return table[key]
ONE=mk('1'); X=mk('x'); Y=mk('y')
def E(a,b): return mk('E',a,b)
def P(t): return E(t,ONE)
Z=E(ONE,E(E(ONE,ONE),ONE))
def L(u): return E(Z,E(E(Z,u),ONE))
def D(u,v): return E(L(u),P(v))
def R(y,t): return E(y,P(t))
def Sub(x,y): return D(R(y,y),R(y,x))
def N(a): return Sub(Z,a)
def S(a,b): return Sub(a,N(b))
def Q(t): return E(t,P(t))
def Mpos(u,v): return P(S(L(u),L(v)))
def M(x,y):
    A=S(Mpos(P(x),P(y)),Mpos(Q(x),Q(y)))
    B=S(Mpos(P(x),Q(y)),Mpos(Q(x),P(y)))
    return Sub(A,B)
def V(x,y):
    q=M(y,y)
    r=P(Sub(L(ONE),L(q)))      # as proposed (L(1))
    return M(M(x,y),r)
def Vz(x,y):
    q=M(y,y)
    r=P(Sub(Z,L(q)))           # optimization: L(1)=Z=0
    return M(M(x,y),r)
from functools import lru_cache
@lru_cache(None)
def size(i):
    k,a,b=nodes[i]
    return 1 if k!='E' else 1+size(a)+size(b)
@lru_cache(None)
def depth(i):
    k,a,b=nodes[i]
    return 0 if k!='E' else 1+max(depth(a),depth(b))
@lru_cache(None)
def leaves(i):
    k,a,b=nodes[i]
    return 1 if k!='E' else leaves(a)+leaves(b)
def xcount(i,name):
    @lru_cache(None)
    def f(j):
        k,a,b=nodes[j]
        if k=='E': return f(a)+f(b)
        return 1 if k==name else 0
    return f(i)
def stats(nm,i):
    print(f"{nm:10s} K(total symbols)={size(i):>10,}  leaves={leaves(i):>9,}  depth={depth(i):>3}  #x={xcount(i,'x'):>6,}  #y={xcount(i,'y'):>6,}  distinct DAG nodes below={0}")
print("P",size(P(X)),"Q",size(Q(X)),"Mpos(x,y)",size(Mpos(X,Y)))
for nm,i in [('Q(x)',Q(X)),('Sub',Sub(X,Y)),('S',S(X,Y)),('Mpos',Mpos(X,Y)),('M',M(X,Y)),('V (propuesta)',V(X,Y)),('V (L(1)->Z)',Vz(X,Y))]:
    stats(nm,i)

# ---- evaluation with memo ----
def evaluate(i,env,E_,exp_ok=True):
    memo={}
    def f(j):
        if j in memo: return memo[j]
        k,a,b=nodes[j]
        if k=='1': v=env['1']
        elif k=='x': v=env['x']
        elif k=='y': v=env['y']
        else: v=E_(f(a),f(b))
        memo[j]=v; return v
    return f(i)


import time

import time
Emp=lambda a,b: mp.e**a - mp.log(b)
def run(root,a,b,dps):
    mp.mp.dps=dps
    env={'1':mp.mpf(1),'x':mp.mpf(a),'y':mp.mpf(b)}
    r=evaluate(root,env,Emp)
    if isinstance(r,mp.mpc): r=r.real
    return r
Mroot=M(X,Y)
print("M(3,3): digits needed")
for d in [100,200,300,320,350,400,500]:
    r=run(Mroot,3,3,d); print(d, mp.nstr(r,12))
print("M(7,7) would need ~", int(( (mp.e**7)*(mp.e**7-7)*2 )/mp.log(10)), "digits (e^B with B=2*P*Q)")
print("M(1,1): B=",mp.nstr(2*mp.e*(mp.e-1),6))
# grid
t0=time.time(); worst=mp.mpf(0)
mp.mp.dps=600
vals=[-3,-2,-1,-0.5,0,0.5,1,2,3,-3.3,2.7]
for a in vals:
    for b in vals:
        env={'1':mp.mpf(1),'x':mp.mpf(a),'y':mp.mpf(b)}
        r=evaluate(Mroot,env,Emp)
        if isinstance(r,mp.mpc): assert abs(r.imag)<mp.mpf(10)**-100; r=r.real
        worst=max(worst,abs(r-mp.mpf(a)*mp.mpf(b)))
print("M grid |.|<=3.3, 600 digits: worst err",mp.nstr(worst,4),f"[{time.time()-t0:.1f}s]")
# V
Vroot=Vz(X,Y); Vp=V(X,Y)
mp.mp.dps=600; worst=mp.mpf(0); t0=time.time()
for a in [-2,-1,0,0.5,1,2]:
    for b in [-2,-1,1,2]:
        env={'1':mp.mpf(1),'x':mp.mpf(a),'y':mp.mpf(b)}
        for root in (Vroot,Vp):
            r=evaluate(root,env,Emp)
            if isinstance(r,mp.mpc): assert abs(r.imag)<mp.mpf(10)**-100; r=r.real
            worst=max(worst,abs(r-mp.mpf(a)/mp.mpf(b)))
print("V (proposal and L(1)->Z), x in [-2,2], y in {+-1,+-2}, 600 digits: worst err",mp.nstr(worst,4),f"[{time.time()-t0:.1f}s]")
