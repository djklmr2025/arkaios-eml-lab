import mpmath as mp, sys
sys.argv=['x']
exec(open('/tmp/eml/opt.py').read().split('if __name__')[0])
mp.mp.dps=400
def ev(root,env):
    memo={}
    def f(j):
        if j in memo: return memo[j]
        k,a,b=nodes[j]
        if k=='1': v=mp.mpf(1)
        elif k in env: v=env[k]
        else:
            A=f(a);B=f(b)
            if mp.im(B)!=0 or mp.re(B)<=0: raise ValueError('log arg <= 0')
            v=mp.e**A-mp.log(B)
        memo[j]=v; return v
    return f(root)
grid=[-30,-12,-6.3,-3,-1,-0.25,0,0.25,1,2.7,3,6.3,12,30]
for name,root,fn in [('Sub K19',SubF(X,Y),lambda a,b:a-b),('Add K19',AddF(X,Y),lambda a,b:a+b)]:
    bad=0;worst=mp.mpf(0)
    for a in grid:
        for b in grid:
            try:
                r=ev(root,{'x':mp.mpf(a),'y':mp.mpf(b)}); worst=max(worst,abs(r-fn(mp.mpf(a),mp.mpf(b))))
            except Exception as e: bad+=1
    print(name,'domain failures',bad,'of',len(grid)**2,'worst err',mp.nstr(worst,3))
Mroot=M_generic(X,Y,SubF,AddF,L1,True)
grid2=[-3,-2,-1,-0.5,0,0.5,1,2,3]
bad=0;worst=mp.mpf(0)
for a in grid2:
    for b in grid2:
        try:
            r=ev(Mroot,{'x':mp.mpf(a),'y':mp.mpf(b)}); worst=max(worst,abs(r-mp.mpf(a)*b))
        except Exception as e: bad+=1
print('M175-class domain failures',bad,'of',len(grid2)**2,'worst err',mp.nstr(worst,3))
