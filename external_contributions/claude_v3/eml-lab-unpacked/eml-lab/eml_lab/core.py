"""Hash-consed EML expression DAG and structural measurements.

A node is ('1',None,None), ('x',None,None), ('y',None,None) or ('E', a, b) meaning eml(a, b) = exp(a) - ln(b).
Identical subexpressions share one node id (hash-consing), so the same object is simultaneously:
  * a TREE   (if you ignore sharing: `size`, `leaves`, `internal` count every occurrence), and
  * a DAG    (`unique_E` counts each distinct E-node once).
Children always have smaller ids than their parents, so ascending id order is a topological order.

Metric glossary (kept separate on purpose):
  K          = total symbols of the tree in RPN (leaves + E-nodes) = 2*leaves - 1   [expression LENGTH]
  unique_E   = number of distinct E-nodes in the DAG                                 [GRAPH compression]
  exp/ln calls: counted by the evaluators, not by structure                          [EXECUTION cost]
"""
import sys
sys.setrecursionlimit(100000)

class Dag:
    def __init__(self):
        self.nodes = []
        self.table = {}
        self.ONE = self._mk('1'); self.X = self._mk('x'); self.Y = self._mk('y')
    def _mk(self, kind, a=None, b=None):
        key = (kind, a, b)
        i = self.table.get(key)
        if i is None:
            i = len(self.nodes); self.nodes.append(key); self.table[key] = i
        return i
    def E(self, a, b):
        return self._mk('E', a, b)

G = Dag()
ONE, X, Y = G.ONE, G.X, G.Y

def E(a, b): return G.E(a, b)
def P(t):    return E(t, ONE)            # exp(t)                    (valid for all real t)
def Q(t):    return E(t, P(t))           # exp(t) - t  >= 1 > 0      (valid for all real t)
Z = E(ONE, E(E(ONE, ONE), ONE))          # the constant 0

_size, _depth, _leaves = {}, {}, {}
def size(i):
    if i in _size: return _size[i]
    k, a, b = G.nodes[i]
    v = 1 if k != 'E' else 1 + size(a) + size(b)
    _size[i] = v; return v
def leaves(i):
    if i in _leaves: return _leaves[i]
    k, a, b = G.nodes[i]
    v = 1 if k != 'E' else leaves(a) + leaves(b)
    _leaves[i] = v; return v
def depth(i):
    if i in _depth: return _depth[i]
    k, a, b = G.nodes[i]
    v = 0 if k != 'E' else 1 + max(depth(a), depth(b))
    _depth[i] = v; return v
def internal(i):
    """number of E-nodes of the TREE (= (K-1)/2) = exp calls = ln calls of a pure tree evaluation"""
    return (size(i) - 1) // 2
def reach(i):
    seen, st = set(), [i]
    while st:
        j = st.pop()
        if j in seen: continue
        seen.add(j)
        k, a, b = G.nodes[j]
        if k == 'E': st += [a, b]
    return seen
def unique_E(i):
    return sum(1 for j in reach(i) if G.nodes[j][0] == 'E')
def count_leaf(i, name):
    """occurrences of leaf `name` ('x','y','1') in the TREE"""
    memo = {}
    def f(j):
        if j in memo: return memo[j]
        k, a, b = G.nodes[j]
        v = f(a) + f(b) if k == 'E' else (1 if k == name else 0)
        memo[j] = v; return v
    return f(i)

def rpn(i):
    out = []
    def go(j):
        k, a, b = G.nodes[j]
        if k == 'E': go(a); go(b); out.append('E')
        else: out.append(k)
    go(i)
    return ''.join(out)
def parse_rpn(s, env=None):
    """RPN string over {1, x, y, E}. `env` maps 'x'/'y' to node ids (default: the leaves X, Y)."""
    env = env or {'x': X, 'y': Y}
    st = []
    for c in s:
        if c == '1': st.append(ONE)
        elif c in env: st.append(env[c])
        elif c == 'E':
            b = st.pop(); a = st.pop(); st.append(E(a, b))
        else: raise ValueError('bad symbol %r' % c)
    if len(st) != 1: raise ValueError('malformed RPN')
    return st[0]
def describe(i):
    return dict(K=size(i), leaves=leaves(i), depth=depth(i), internal=internal(i),
                unique_E=unique_E(i), x_leaves=count_leaf(i, 'x'), y_leaves=count_leaf(i, 'y'))
