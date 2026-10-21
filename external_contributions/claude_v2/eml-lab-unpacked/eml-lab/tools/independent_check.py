#!/usr/bin/env python3
"""INDEPENDENT checker: shares no code with eml_lab. Reads an RPN file (symbols 1 x y E), evaluates it as a pure
stack machine (no sharing, no rewriting) with mpmath, verifies that every ln argument is > 0, and compares with
the target function. Use it to cross-check results without trusting the DAG/evaluator code.

  python tools/independent_check.py expressions/M_opt.rpn mul  --dps 450 --points "3,3;-2,0.5;0,1"
  python tools/independent_check.py expressions/V_opt.rpn div  --dps 300 --points "1.5,2;-2,0.5"
targets: sub add mul div
"""
import argparse, sys, time
import mpmath as mp
ap = argparse.ArgumentParser(); ap.add_argument('rpn'); ap.add_argument('target', choices=['sub', 'add', 'mul', 'div'])
ap.add_argument('--dps', type=int, default=450); ap.add_argument('--points', default='3,3;-2,0.5;0,1;1,1')
a = ap.parse_args(); mp.mp.dps = a.dps
prog = open(a.rpn).read().strip()
T = {'sub': lambda x, y: x - y, 'add': lambda x, y: x + y, 'mul': lambda x, y: x * y, 'div': lambda x, y: x / y}[a.target]
ok = True
for pt in a.points.split(';'):
    xs, ys = pt.split(','); x, y = mp.mpf(xs), mp.mpf(ys)
    t0 = time.time(); st = []
    try:
        for c in prog:
            if c == '1': st.append(mp.mpf(1))
            elif c == 'x': st.append(x)
            elif c == 'y': st.append(y)
            else:
                b = st.pop(); aa = st.pop()
                if not b > 0: raise ArithmeticError('ln of non-positive: %s' % mp.nstr(b, 6))
                st.append(mp.exp(aa) - mp.log(b))
        v = st.pop(); assert not st
        err = abs(v - T(x, y)); good = err < mp.mpf(10) ** -20
        print(f"({xs},{ys})  value={mp.nstr(v, 20)}  abs_err={mp.nstr(err, 3)}  {'OK' if good else 'MISMATCH (maybe too few digits: raise --dps)'}  [{time.time()-t0:.1f}s]")
        ok &= good
    except ArithmeticError as e:
        print(f"({xs},{ys})  DOMAIN FAIL: {e}"); ok = False
sys.exit(0 if ok else 1)
