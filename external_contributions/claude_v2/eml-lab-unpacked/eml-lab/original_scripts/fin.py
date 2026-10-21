import numpy as np, sys
exec(open('/tmp/eml/opt.py').read().split('if __name__')[0])
np.seterr(all='ignore')
Mnew=lambda a,b:M_generic(a,b,SubF,AddF,L1,True)
Mfull=Mnew(X,Y)
q=Mnew(Y,Y)
r=P(SubF(Z,L1(q)))
V=Mnew(Mnew(X,Y),r)
V2=Mnew(X,Mnew(Y,r))
for nm,i in [('M (new, K631 class)',Mfull),('V = M(M(x,y),1/y^2)',V),('V2 = M(x, M(y,1/y^2))',V2)]:
    stats(nm,i)
def evf(root,x,y):
    memo={}
    def f(j):
        if j in memo: return memo[j]
        k,a,b=nodes[j]
        if k=='1': v=np.float64(1)
        elif k=='x': v=np.float64(x)
        elif k=='y': v=np.float64(y)
        else: v=np.exp(f(a))-np.log(f(b))
        memo[j]=v; return v
    return f(root)
grid=np.arange(-8,8.01,0.25); ok=0;tot=0;okp=[]
for a in grid:
    for b in grid:
        r_=evf(Mfull,a,b); t=a*b; tot+=1
        if np.isfinite(r_) and abs(r_-t)<=1e-6*max(1,abs(t)): ok+=1; okp.append((a,b))
okp=np.array(okp)
print("M new float64 ok:",ok,"of",tot,"; x range",okp[:,0].min(),okp[:,0].max(),"y range",okp[:,1].min(),okp[:,1].max())
for a,b in [(1,1),(0.5,0.5),(2,3),(-3,-3),(-6,2),(3,-3),(1.5,1.5),(2,2)]:
    print(f"M({a},{b})={evf(Mfull,a,b)} true={a*b}")
Vz=V
for a,b in [(1,1),(1,2),(-1,2),(2,-1),(0.5,0.5)]:
    print(f"V({a},{b})={evf(V,a,b)}  V2={evf(V2,a,b)} true={a/b}")
