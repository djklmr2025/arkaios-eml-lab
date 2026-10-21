"""Priority D. Three EXECUTION strategies on the SAME expression, measured separately from length and from accuracy.
Columns: K (length) | unique_E (graph) | exp/ln calls and node evaluations (execution) | seconds | result (accuracy, last)"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import numpy as np
from eml_lab.constructions import CATALOG
from eml_lab.core import size, unique_E
from eml_lab.evaluators import evaluate, Stats
x, y = 0.5, 0.5
env = {'x': np.float64(x), 'y': np.float64(y)}
print(f"float64, point (x,y)=({x},{y}); true: sub={x-y} add={x+y} mul={x*y} div={x/y}\n")
print(f"{'expr':9s} {'strategy':11s} {'K':>10s} {'unique_E':>8s} {'exp calls':>10s} {'ln calls':>9s} {'node evals':>10s} {'seconds':>9s}  result")
for name in ('Sub19', 'Add19', 'M_opt', 'V_opt', 'M_orig'):
    root = CATALOG[name][0]()
    for strat in ('tree', 'dag', 'dag_stable'):
        st = Stats(); v = evaluate(root, env, 'f64', strat, st)
        print(f"{name:9s} {strat:11s} {size(root):>10,} {unique_E(root):>8,} {st.exp_calls:>10,} {st.ln_calls:>9,} {st.node_evals:>10,} {st.seconds:>9.4f}  {v!r}")
print("\nReading guide: K does not change with the strategy; exp/ln calls do. 'result' is reported last on purpose:")
print("a cheaper strategy is NOT evidence of a better answer, and a wrong float64 answer says nothing about K or call counts.")
