"""Write the COMPLETE expressions (RPN over {1,x,y,E}) + DAG JSON + manifest with SHA-256 into expressions/."""
import os, sys, json, hashlib
ROOT = os.path.join(os.path.dirname(__file__), '..'); sys.path.insert(0, ROOT)
from eml_lab.constructions import CATALOG
from eml_lab.core import rpn, describe, reach, G
out = os.path.join(ROOT, 'expressions'); os.makedirs(out, exist_ok=True)
manifest = {}
for name, (build, _) in CATALOG.items():
    root = build(); s = rpn(root)
    open(os.path.join(out, name + '.rpn'), 'w').write(s + '\n')
    ids = sorted(reach(root)); remap = {j: n for n, j in enumerate(ids)}
    dag = [[k, remap.get(a), remap.get(b)] for k, a, b in (G.nodes[j] for j in ids)]
    json.dump({'root': remap[root], 'nodes': dag, 'meaning': "node ['E',a,b] = exp(a) - ln(b); leaves '1','x','y'"},
              open(os.path.join(out, name + '.dag.json'), 'w'))
    d = describe(root); d['sha256_rpn'] = hashlib.sha256(s.encode()).hexdigest(); d['rpn_length'] = len(s)
    assert len(s) == d['K']
    manifest[name] = d
    print(f"{name:9s} K={d['K']:>11,}  sha256={d['sha256_rpn'][:16]}...")
json.dump(manifest, open(os.path.join(out, 'manifest.json'), 'w'), indent=1)
print("\nSub19 RPN :", open(os.path.join(out, 'Sub19.rpn')).read().strip())
print("Add19 RPN :", open(os.path.join(out, 'Add19.rpn')).read().strip())
print("M_opt RPN :", open(os.path.join(out, 'M_opt.rpn')).read().strip())
print("(V_opt RPN is 88,715 symbols: expressions/V_opt.rpn)")
