import mpmath as mp
mp.mp.dps = 80
def E(a,b): return mp.e**a - mp.log(b)

# Tree representation for expansion: ('1',) or ('E', l, r)
ONE=('1',)
def T(l,r): return ('E',l,r)
def size(t): return 1 if t[0]=='1' else 1+size(t[1])+size(t[2])
def depth(t): return 0 if t[0]=='1' else 1+max(depth(t[1]),depth(t[2]))
def leaves(t): return 1 if t[0]=='1' else leaves(t[1])+leaves(t[2])
# symbolic vars as ('v',name)
def V(n): return ('v',n)
def size(t):
    if t[0] in('1','v'): return 1
    return 1+size(t[1])+size(t[2])
def depth(t):
    if t[0] in('1','v'): return 0
    return 1+max(depth(t[1]),depth(t[2]))
def leaves(t):
    if t[0] in('1','v'): return 1
    return leaves(t[1])+leaves(t[2])
def ev(t,env):
    if t[0]=='1': return mp.mpf(1)
    if t[0]=='v': return env[t[1]]
    return E(ev(t[1],env),ev(t[2],env))
def sub(t,old,new):
    if t[0]=='1': return t
    if t[0]=='v': return new if t[1]==old else t
    return ('E',sub(t[1],old,new),sub(t[2],old,new))

def P(t): return T(t,ONE)
Z=T(ONE,T(T(ONE,ONE),ONE))
def L(u): return T(Z,T(T(Z,u),ONE))
def D(u,v): return T(L(u),P(v))
def R(y,t): return T(y,P(t))
def Sub(x,y): return D(R(y,y),R(y,x))
x,y=V('x'),V('y')
S1=Sub(x,y)
N=lambda a: Sub(Z,a)
Add=Sub(x,N(y))
for name,t in [('Z',Z),('P',P(x)),('L',L(x)),('Sub',S1),('Neg',N(x)),('Add',Add)]:
    print(name,'nodes',size(t),'leaves',leaves(t),'depth',depth(t))

# exact tests (mpmath, real)
import itertools
vals=[-50,-10,-3.5,-1,-1e-9,0,1e-9,1,2.5,10,50]
maxerr=0
for a in vals:
    for b in vals:
        a_,b_=mp.mpf(a),mp.mpf(b)
        env={'x':a_,'y':b_}
        try:
            r=ev(S1,env); r2=ev(Add,env)
            e1=abs(r-(a_-b_)); e2=abs(r2-(a_+b_))
            maxerr=max(maxerr,e1,e2)
            if abs(r.imag if hasattr(r,'imag') else 0)>0: print('complex',a,b)
        except Exception as ex:
            print('fail',a,b,ex)
print('max error 80-digit:',mp.nstr(maxerr,5))
print('Z=',ev(Z,{}))

print("---- RPN of Sub ----")
def rpn(t):
    if t[0]=='1': return '1'
    if t[0]=='v': return t[1]
    return rpn(t[1])+rpn(t[2])+'E'
r=rpn(S1); print(r, len(r))
print("Z RPN:",rpn(Z), len(rpn(Z)))
print("L(x) RPN:",rpn(L(x)), len(rpn(L(x))))
print("paper ln RPN: 11xE1EE (7)")

# complex product / division test
mp.mp.dps=60
Mul=P(Add)  # placeholder to define below
def subst(t,env): return t
AddT=lambda a,b: Sub(a,N(b))
MulT=P(AddT(L(x),L(y)))
DivT=P(Sub(L(x),L(y)))
print("Mul nodes",size(MulT),"Div nodes",size(DivT))
vals=[-7.5,-2,-1,-0.1,0.1,1,3,12]
me=0;de=0
for a in vals:
    for b in vals:
        env={'x':mp.mpf(a),'y':mp.mpf(b)}
        m=ev(MulT,env); d=ev(DivT,env)
        me=max(me,abs(m-mp.mpf(a)*b)); de=max(de,abs(d-mp.mpf(a)/b))
print("max err Mul (incl negatives, complex principal log):",mp.nstr(me,5))
print("max err Div:",mp.nstr(de,5))
print("sample (-2)*(-3) ->",mp.nstr(ev(MulT,{'x':mp.mpf(-2),'y':mp.mpf(-3)}),15))
try:
    print(ev(MulT,{'x':mp.mpf(0),'y':mp.mpf(3)}))
except Exception as ex: print("x=0 in mpmath:",type(ex).__name__)
