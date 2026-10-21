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



import numpy as np
def Ef(a,b):
    with np.errstate(all='ignore'): return np.exp(a)-np.log(b)
def evf(root,x,y):
    return evaluate(root,{'1':np.float64(1),'x':np.float64(x),'y':np.float64(y)},Ef)
Mroot=M(X,Y); Vroot=Vz(X,Y)
print("M(0,0)",evf(Mroot,0.0,0.0),"M(1,1)",evf(Mroot,1.0,1.0),"M(2,3)",evf(Mroot,2.0,3.0),"M(-1,-1)",evf(Mroot,-1.0,-1.0),"M(-2,3)",evf(Mroot,-2.0,3.0),"M(0.5,0.5)",evf(Mroot,.5,.5))
grid=np.arange(-8,8.01,0.25)
ok=0; tot=0; okpts=[]
for a in grid:
    for b in grid:
        r=evf(Mroot,a,b); t=a*b; tot+=1
        if np.isfinite(r) and abs(r-t)<=1e-6*max(1,abs(t)): ok+=1; okpts.append((a,b))
print("M float64 correct (rel/abs 1e-6): %d of %d"%(ok,tot))
okpts=np.array(okpts)
print("x range ok:",okpts[:,0].min(),okpts[:,0].max()," y range ok:",okpts[:,1].min(),okpts[:,1].max())
print("max x+y among ok points:",(okpts[:,0]+okpts[:,1]).max())
# how does the success region look along diagonal / negative
for a,b in [(0.5,0.5),(0.75,0.75),(1,1),(1,0),(0,3),(-3,-3),(-6,-6),(-8,-8),(-6,2),(-6,6),(3,-3)]:
    r=evf(Mroot,a,b); print(f"M({a},{b})={r} true={a*b}")
for x,y in [(1,1),(1,2),(-1,2),(2,-1),(0.5,0.5)]:
    print(f"V({x},{y})={evf(Vroot,x,y)} true={x/y}")
