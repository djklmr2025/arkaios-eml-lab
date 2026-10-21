import numpy as np, sys, time, pickle
np.seterr(all='ignore')
NMAX=int(sys.argv[1]) if len(sys.argv)>1 else 7
pts=np.array([(-4.3,1.9),(3.7,-2.6),(4.8,3.9),(-1.9,-4.4),(1.1,0.35),(-0.4,0.8),(2.2,-4.9),(-5.1,-0.7)])
m=len(pts); X=pts[:,0]; Y=pts[:,1]
R=np.random.default_rng(1).integers(1,2**61,size=m,dtype=np.int64)
def H(V): return (np.round(np.sign(V)*np.log1p(np.abs(V))*1e7).astype(np.int64)*R).sum(axis=1)
vecs={1:np.array([np.ones(m),X,Y])}
back={1:[('1',),('x',),('y',)]}
hashes={1:H(vecs[1])}
seen=np.sort(hashes[1].copy())
def has(h,arr):  # arr sorted
    pos=np.searchsorted(arr,h); pos[pos==len(arr)]=0
    return arr[pos]==h
t0=time.time()
for n in range(2,NMAX+1):
    newV=[];newB=[];newH=[]
    for i in range(1,n):
        j=n-i
        A=vecs[i]; B=vecs[j]
        okB=(B>0).all(axis=1); Bi=np.nonzero(okB)[0]; logB=np.log(B[Bi])
        expA=np.exp(A); okA=np.isfinite(expA).all(axis=1); Ai=np.nonzero(okA)[0]; expA=expA[Ai]
        if len(Ai)==0 or len(Bi)==0: continue
        ch=max(1,int(3e6//(len(Bi)*m)))
        for s in range(0,len(Ai),ch):
            e=expA[s:s+ch]
            V=(e[:,None,:]-logB[None,:,:]).reshape(-1,m)
            ia=np.repeat(Ai[s:s+ch],len(Bi)); ib=np.tile(Bi,len(e))
            good=np.isfinite(V).all(axis=1)&(np.abs(V).max(axis=1)<1e250)
            V=V[good]; ia=ia[good]; ib=ib[good]
            if len(V)==0: continue
            h=H(V)
            u,idx=np.unique(h,return_index=True)
            keep=~has(u,seen)
            u=u[keep]; idx=idx[keep]
            if len(u)==0: continue
            # also remove ones already queued this level
            if newH:
                q=np.sort(np.concatenate(newH)); k2=~has(u,q); u=u[k2]; idx=idx[k2]
            if len(u)==0: continue
            newV.append(V[idx]); newH.append(u)
            newB.append(np.stack([np.full(len(idx),i),ia[idx],np.full(len(idx),j),ib[idx]],axis=1))
    if newV:
        vecs[n]=np.concatenate(newV); hashes[n]=np.concatenate(newH); back[n]=np.concatenate(newB)
        seen=np.sort(np.concatenate([seen,hashes[n]]))
    else:
        vecs[n]=np.zeros((0,m)); hashes[n]=np.zeros(0,dtype=np.int64); back[n]=np.zeros((0,4),dtype=np.int64)
    print(f"n={n} leaves (K={2*n-1}): distinct new functions={len(vecs[n]):,}  total={len(seen):,}  [{time.time()-t0:.0f}s]",flush=True)
pickle.dump((NMAX,pts,vecs,hashes,back),open(f'/tmp/eml/tablesW{NMAX}.pkl','wb'))
print("saved")
