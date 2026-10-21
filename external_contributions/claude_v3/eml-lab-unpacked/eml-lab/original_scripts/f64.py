import math, warnings
warnings.filterwarnings('ignore')
import numpy as np
def E(a,b):
    with np.errstate(all='ignore'):
        return np.exp(a)-np.log(b)
one=1.0
P=lambda t:E(t,one)
Z=E(one,E(E(one,one),one))
L=lambda u:E(Z,E(E(Z,u),one))
D=lambda u,v:E(L(u),P(v))
R=lambda y,t:E(y,P(t))
Sub=lambda x,y:D(R(y,y),R(y,x))
Add=lambda x,y:Sub(x,Sub(Z,y))
print("Z float64 =",Z)
bad=[]
tests=[0,1,-1,0.5,-0.5,2,-2,5,-5,6,6.5,7,10,-10,20,-20,100,-100,700,-700,1e-12,1e6]
for a in tests:
    for b in tests:
        r=Sub(a,b); t=a-b
        ok = np.isfinite(r) and abs(r-t)<=1e-6*max(1,abs(t))
        if not ok: bad.append((a,b,float(r),t))
print("Sub failures in float64:",len(bad),"of",len(tests)**2)
for z in bad[:12]: print(z)
# find y threshold
for y in [5,6,6.4,6.5,6.6,7]:
    print("y=",y,"Sub(1,y)=",Sub(1.0,y),"true",1-y)
for x in [0,-1,-5,-10]:
    print("x=",x,"Sub(x,0)=",Sub(float(x),0.0))
# small-range accuracy
rng=np.random.default_rng(0)
xs=rng.uniform(-5,5,10000); ys=rng.uniform(-5,5,10000)
err=np.abs(Sub(xs,ys)-(xs-ys)); print("max abs err |x|,|y|<5:",err.max())
err=np.abs(Add(xs,ys)-(xs+ys)); print("Add max abs err:",err.max())
