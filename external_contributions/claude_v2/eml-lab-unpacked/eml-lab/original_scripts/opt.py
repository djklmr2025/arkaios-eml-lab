import sys, mpmath as mp
from functools import lru_cache
sys.setrecursionlimit(100000)
nodes=[]; table={}
def mk(k,a=None,b=None):
    key=(k,a,b)
    if key in table: return table[key]
    nodes.append(key); table[key]=len(nodes)-1; return table[key]
ONE=mk('1'); X=mk('x'); Y=mk('y')
def E(a,b): return mk('E',a,b)
P=lambda t:E(t,ONE)
Z=E(ONE,E(E(ONE,ONE),ONE))
# --- original construction (Z-based ln, Sub via R_y)
def L0(u): return E(Z,E(E(Z,u),ONE))
def Sub0(x,y):
    R=lambda t:E(y,P(t)); return E(L0(R(y)),P(R(x)))
# --- optimized: paper ln (uses 1), same Sub structure
def L1(u): return E(ONE,E(E(ONE,u),ONE))
def Sub1(x,y):
    R=lambda t:E(y,P(t)); return E(L1(R(y)),P(R(x)))
def N1(a): return Sub1(Z,a)
def S1(a,b): return Sub1(a,N1(b))
# --- exhaustive-search real-only formulas (K=19): x-y = 111y1EEE1EE1x1EE1EE
def parse(s,env):
    st=[]
    for c in s:
        if c=='1': st.append(ONE)
        elif c in env: st.append(env[c])
        else: b=st.pop(); a=st.pop(); st.append(E(a,b))
    assert len(st)==1; return st[0]
SUBS="11yy1EEE1EEyx1EE1EE"
def SubF(a,b): return parse(SUBS,{'x':a,'y':b})
ADDS="x11xx1EEE1EEy1EE1EE"
def AddF(a,b): return parse(ADDS,{'x':a,'y':b})
def ln(u): return L1(u)
Q=lambda t:E(t,P(t))
# M with generic L
def M_generic(x,y,Sub,S,L,Mpos_shortcut=False):
    Px,Py,Qx,Qy=P(x),P(y),Q(x),Q(y)
    if not Mpos_shortcut:
        Mp=lambda u,v:P(S(L(u),L(v)))
        A=S(Mp(Px,Py),Mp(Qx,Qy)); B=S(Mp(Px,Qy),Mp(Qx,Py))
    else:
        lx,ly=L(Qx),L(Qy)          # ln(P(t))=t is free
        A=S(P(S(x,y)),P(S(lx,ly))); B=S(P(S(x,ly)),P(S(lx,y)))
    return Sub(A,B)
@lru_cache(None)
def size(i):
    k,a,b=nodes[i]; return 1 if k!='E' else 1+size(a)+size(b)
@lru_cache(None)
def depth(i):
    k,a,b=nodes[i]; return 0 if k!='E' else 1+max(depth(a),depth(b))
@lru_cache(None)
def uniq(i):
    # set of unique node ids reachable
    pass
def reach(i):
    seen=set(); st=[i]
    while st:
        j=st.pop()
        if j in seen: continue
        seen.add(j); k,a,b=nodes[j]
        if k=='E': st+= [a,b]
    return seen
def stats(name,i):
    r=reach(i); inner=[j for j in r if nodes[j][0]=='E']
    # nodes that depend on variables
    @lru_cache(None)
    def dep(j):
        k,a,b=nodes[j]
        if k in('x','y'): return True
        if k=='1': return False
        return dep(a) or dep(b)
    vd=[j for j in inner if dep(j)]
    K=size(i)
    print(f"{name:34s} K={K:>12,} | unique E-nodes={len(inner):>6,} (var-dependent {len(vd):>6,}) | exp/ln evals tree={(K-1)//2:>10,} DAG={len(inner):>6,} | depth={depth(i)}")
    return len(inner)
if __name__=="__main__":
    print("--- sub/add/neg ---")
    stats("Sub original (Z-ln)",Sub0(X,Y))
    stats("Sub with paper ln (K)",Sub1(X,Y))
    stats("Sub exhaustive real-only",SubF(X,Y))
    stats("Add via Sub1,N1",S1(X,Y))
    stats("Add exhaustive real-only",AddF(X,Y))
    print("--- products ---")
    stats("M original (Z-ln, Mpos full)",M_generic(X,Y,Sub0,lambda a,b:Sub0(a,Sub0(Z,b)),L0))
    stats("M: paper ln + Sub1/S1",M_generic(X,Y,Sub1,S1,L1))
    stats("M: +exhaustive Sub/Add",M_generic(X,Y,SubF,AddF,L1))
    stats("M: +exhaustive +ln(P(t))=t shortcut",M_generic(X,Y,SubF,AddF,L1,True))
