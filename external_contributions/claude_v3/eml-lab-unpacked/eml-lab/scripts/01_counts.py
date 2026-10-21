"""Structural measurements for every construction: K, leaves, depth, unique E-nodes (DAG), #x/#y leaves.
Expected: see results/01_counts.txt and README."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from eml_lab.constructions import CATALOG
from eml_lab.core import describe
print(f"{'name':9s} {'K (symbols)':>13s} {'leaves':>11s} {'depth':>5s} {'tree E-nodes':>13s} {'unique E (DAG)':>14s} {'#x':>9s} {'#y':>9s}")
for name, (build, _) in CATALOG.items():
    d = describe(build())
    print(f"{name:9s} {d['K']:>13,} {d['leaves']:>11,} {d['depth']:>5} {d['internal']:>13,} {d['unique_E']:>14,} {d['x_leaves']:>9,} {d['y_leaves']:>9,}")
print("\nNote: K = 2*leaves-1 is the RPN length used by Odrzywolek's Table 4. 'tree E-nodes' = exp calls = ln calls of a pure tree run.")
