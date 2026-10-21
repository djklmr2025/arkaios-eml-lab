import numpy as np, pickle, sys, time, mpmath as mp
np.seterr(all='ignore')
NMAX,pts,vecs,hashes,back=pickle.load(open('/tmp/eml/tablesW13.pkl','rb'))
m=len(pts); X=pts[:,0]; Y=pts[:,1]
R=np.random.default_rng(1).integers(1,2**61,size=m,dtype=np.int64)
def H(V): return (np.round(np.sign(V)*np.log1p(np.abs(V))*1e7).astype(np.int64)*R).sum(axis=1)
order={n:np.argsort(hashes[n]) for n in range(1,NMAX+1)}
sh={n:hashes[n][order[n]] for n in range(1,NMAX+1)}
def lookup(n,h):
    s=sh[n]
    if len(s)==0: return np.full(len(h),-1)
    pos=np.searchsorted(s,h); pos[pos==len(s)]=0
    f=s[pos]==h
    out=np.where(f,order[n][pos],-1); return out
def rpn(n,idx):
    if n==1: return back[1][idx][0]
    i,ia,j,ib=back[n][idx]
    return rpn(i,ia)+rpn(j,ib)+'E'
def search(T,name,maxn=26):
    h=H(T[None,:])
    for n in range(1,NMAX+1):
        r=lookup(n,h)
        if r[0]>=0: return n,rpn(n,r[0])
    for n in range(NMAX+1,maxn+1):
        for i in range(max(1,n-NMAX),min(NMAX,n-1)+1):
            j=n-i
            if i<1 or j<1 or i>NMAX or j>NMAX: continue
            if len(vecs[i])<=len(vecs[j]):
                A=vecs[i]; eA=np.exp(A)
                ok=np.isfinite(eA).all(axis=1)
                with np.errstate(all='ignore'):
                    arg=np.exp(A)-T[None,:]   # = ln b -> b=exp(arg)
                    Bv=np.exp(arg)
                good=ok&np.isfinite(Bv).all(axis=1)&(Bv>0).all(axis=1)&(np.abs(Bv).max(axis=1)<1e250)
                idxA=np.nonzero(good)[0]
                if len(idxA)==0: continue
                r=lookup(j,H(Bv[idxA]))
                hit=np.nonzero(r>=0)[0]
                if len(hit): 
                    a=idxA[hit[0]]; b=r[hit[0]]
                    return n,rpn(i,a)+rpn(j,b)+'E'
            else:
                B=vecs[j]; okB=(B>0).all(axis=1); idxB=np.nonzero(okB)[0]
                with np.errstate(all='ignore'):
                    arg=T[None,:]+np.log(B[idxB])
                good=(arg>0).all(axis=1)
                idxB=idxB[good]; av=np.log(arg[good])
                if len(idxB)==0: continue
                r=lookup(i,H(av))
                hit=np.nonzero(r>=0)[0]
                if len(hit):
                    return n,rpn(i,r[hit[0]])+rpn(j,idxB[hit[0]])+'E'
    return None,None
targets={'x-y':X-Y,'x+y':X+Y,'-x':-X,'y-x':Y-X,'x*y':X*Y,'x/y':X/Y,'1/x':1/X,'x^2':X**2,'2x':2*X,'x/2':X/2,'-1':-np.ones(m),'2':2*np.ones(m),'0':np.zeros(m),'x*y/(x+y... skip':None}
res={}
for k,T in targets.items():
    if T is None: continue
    t0=time.time(); n,s=search(T,k)
    res[k]=(n,s)
    print(f"{k:8s} leaves={n} K={None if n is None else 2*n-1}  RPN={s if s is None or len(s)<80 else s[:60]+'...'} [{time.time()-t0:.0f}s]",flush=True)
pickle.dump(res,open('/tmp/eml/resW.pkl','wb'))
