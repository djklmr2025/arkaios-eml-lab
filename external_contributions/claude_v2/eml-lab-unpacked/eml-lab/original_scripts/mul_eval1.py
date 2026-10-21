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
mp.mp.dps=250
Emp=lambda a,b: mp.e**a - mp.log(b)
def tst(root,fn,vx,vy,label):
    t0=time.time(); worst=mp.mpf(0); fails=[]
    for a in vx:
        for b in vy:
            env={'1':mp.mpf(1),'x':mp.mpf(a),'y':mp.mpf(b)}
            try:
                r=evaluate(root,env,Emp)
                if isinstance(r,mp.mpc):
                    if abs(r.imag)>mp.mpf(10)**-40: raise ValueError('complex')
                    r=r.real
                err=abs(r-fn(mp.mpf(a),mp.mpf(b)))
            except Exception as ex:
                fails.append((a,b,str(ex)[:50])); continue
            worst=max(worst,err)
    print(f"{label}: worst abs err={mp.nstr(worst,4)} failures={len(fails)} {fails[:3]} [{time.time()-t0:.1f}s]",flush=True)
vals=[-2,-1,-0.5,0,0.5,1,2]
tst(M(X,Y),lambda a,b:a*b,vals,vals,"M  x,y in [-2,2] (250 dig)")
tst(M(X,Y),lambda a,b:a*b,[-3,3,1.5],[-3,3,-0.7],"M  |x|,|y|<=3 (250 dig)")
