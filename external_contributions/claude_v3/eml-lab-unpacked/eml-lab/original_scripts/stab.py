import numpy as np, mpmath as mp
exec(open('/tmp/eml/opt.py').read().split('if __name__')[0])
np.seterr(all='ignore')
Mn=lambda a,b:M_generic(a,b,SubF,AddF,L1,True)
Mfull=Mn(X,Y)
q=Mn(Y,Y); r=P(SubF(Z,L1(q))); V=Mn(Mn(X,Y),r)
def isP(j):
    k,a,b=nodes[j]; return k=='E' and nodes[b][0]=='1'
def evf(root,x,y,stable):
    memo={}
    def f(j):
        if j in memo: return memo[j]
        k,a,b=nodes[j]
        if k=='1': v=np.float64(1)
        elif k=='x': v=np.float64(x)
        elif k=='y': v=np.float64(y)
        else:
            if stable and isP(b):          # E(a, exp(w)) = exp(a) - w   (exact on the reals)
                w=f(nodes[b][1]); v=np.exp(f(a))-w
            else: v=np.exp(f(a))-np.log(f(b))
        memo[j]=v; return v
    return f(root)
def score(root,fn,grid_x,grid_y,stable,tol=1e-6):
    ok=0;tot=0
    for a in grid_x:
        for b in grid_y:
            r_=evf(root,a,b,stable); t=fn(a,b); tot+=1
            if np.isfinite(r_) and abs(r_-t)<=tol*max(1,abs(t)): ok+=1
    return ok,tot
g=np.arange(-8,8.01,0.25)
print("M plain  float64:",score(Mfull,lambda a,b:a*b,g,g,False))
print("M stable float64:",score(Mfull,lambda a,b:a*b,g,g,True))
for tol in (1e-9,1e-12):
    print(f"M stable tol {tol}:",score(Mfull,lambda a,b:a*b,g,g,True,tol))
# where does it fail?
for a,b in [(1,1),(2,2),(3,3),(5,5),(-8,-8),(-6,2),(3,-3),(7,-7),(8,8),(10,10)]:
    print(f"M({a},{b}) plain={evf(Mfull,a,b,False)}  stable={evf(Mfull,a,b,True)}  true={a*b}")
# V
gv=[(x,y) for x in (-3,-1,0,0.5,1,2,3) for y in (-3,-2,-1,-0.5,0.5,1,2,3)]
okp=0;oks=0
for a,b in gv:
    okp+= np.isfinite(evf(V,a,b,False)) and abs(evf(V,a,b,False)-a/b)<1e-6*max(1,abs(a/b))
    oks+= np.isfinite(evf(V,a,b,True)) and abs(evf(V,a,b,True)-a/b)<1e-6*max(1,abs(a/b))
print("V plain ok:",okp,"of",len(gv)," stable ok:",oks)
for a,b in [(1,1),(1,2),(-1,2),(2,-1),(0.5,0.5),(3,0.5)]:
    print(f"V({a},{b}) stable={evf(V,a,b,True)} true={a/b}")
# exp / ln call counts in memoized evaluation (stable): each unique E node = 1 exp; ln only if b is not exp-node
def counts(root):
    seen=set();st=[root];E_=0;ln=0;skipped=0
    while st:
        j=st.pop()
        if j in seen: continue
        seen.add(j); k,a,b=nodes[j]
        if k=='E':
            E_+=1
            if isP(j) and False: pass
            if isP(b): skipped+=1
            else: ln+=1
            st+=[a,b]
    return E_,ln,skipped
print("unique E, ln calls after rewrite, ln eliminated:",counts(Mfull),counts(V))
