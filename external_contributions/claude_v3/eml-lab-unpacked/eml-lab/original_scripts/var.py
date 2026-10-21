exec(open('/tmp/eml/opt.py').read().split('if __name__')[0])
Mn=lambda a,b:M_generic(a,b,SubF,AddF,L1,True)
q=Mn(Y,Y); r=P(SubF(Z,L1(q)))
cands={'M(M(x,y),r)':Mn(Mn(X,Y),r),'M(r,M(x,y))':Mn(r,Mn(X,Y)),'M(M(y,x),r)':Mn(Mn(Y,X),r),'M(r,M(y,x))':Mn(r,Mn(Y,X)),
       'M(M(x,r),y)':Mn(Mn(X,r),Y),'M(y,M(x,r))':Mn(Y,Mn(X,r)),'M(x,M(r,y))':Mn(X,Mn(r,Y)),'M(M(r,x),y)':Mn(Mn(r,X),Y)}
for k,v in sorted(cands.items(),key=lambda kv:size(kv[1])): print(f"{k:14s} K={size(v):>10,} depth={depth(v)}")
print("M(x,y) K=",size(Mn(X,Y)),"M(y,x) K=",size(Mn(Y,X)))
