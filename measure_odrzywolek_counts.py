"""
Script to measure exact node counts, symbol counts, and DAG sharing
of Odrzywolek's compiler (eml_compiler_v4.py).
"""

import re

def EML(a, b):        return f"EML[{a},{b}]"
def eml_exp(z):       return EML(z, "1")
def eml_log(z):       return EML("1", eml_exp(EML("1", z)))
def eml_zero():       return eml_log("1")
def eml_sub(a, b):    return EML(eml_log(a), eml_exp(b))
def eml_neg(z):       return eml_sub(eml_zero(), z)
def eml_add(a, b):    return eml_sub(a, eml_neg(b))
def eml_inv(z):       return eml_exp(eml_neg(eml_log(z)))
def eml_mul(a, b):    return eml_exp(eml_add(eml_log(a), eml_log(b)))
def eml_div(a, b):    return eml_mul(a, eml_inv(b))
def eml_sinh(z):
    e2z = eml_exp(eml_add(z, z))
    ez = eml_exp(z)
    two = eml_add("1", "1")
    return eml_div(eml_sub(e2z, "1"), eml_mul(two, ez))

class Node:
    def __init__(self, key):
        self.key = key

class OpNode(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        super().__init__(f"EML[{left.key},{right.key}]")

    def collect(self, s):
        if self.key not in s:
            s.add(self.key)
            self.left.collect(s)
            self.right.collect(s)

class LeafNode(Node):
    def collect(self, s):
        s.add(self.key)

def parse_to_dag(s):
    # recursive parser of EML string to DAG
    s = s.strip()
    if s == "1":
        return LeafNode("1")
    if s == "x":
        return LeafNode("x")
    if s == "y":
        return LeafNode("y")
    if s == "z":
        return LeafNode("z")
    if s.startswith("EML[") and s.endswith("]"):
        inner = s[4:-1]
        # find comma at top level
        depth = 0
        comma_idx = -1
        for i, c in enumerate(inner):
            if c == '[': depth += 1
            elif c == ']': depth -= 1
            elif c == ',' and depth == 0:
                comma_idx = i
                break
        if comma_idx != -1:
            left_str = inner[:comma_idx]
            right_str = inner[comma_idx+1:]
            return OpNode(parse_to_dag(left_str), parse_to_dag(right_str))
    return LeafNode(s)

fns = [
    ("1", "1"),
    ("e", eml_exp("1")),
    ("0", eml_zero()),
    ("ln(x)", eml_log("x")),
    ("exp(x)", eml_exp("x")),
    ("x - y", eml_sub("x", "y")),
    ("-x", eml_neg("x")),
    ("x + y", eml_add("x", "y")),
    ("1/x", eml_inv("x")),
    ("x * y", eml_mul("x", "y")),
    ("x / y", eml_div("x", "y")),
    ("sinh(x)", eml_sinh("x"))
]

print("=" * 115)
print(f"{'Función':<12} | {'EML Nodes (Tree)':<18} | {'Total Symb (Tree)':<18} | {'Unique Nodes (DAG)':<20} | {'Ratio Tree/DAG':<15} | {'String Length'}")
print("=" * 115)

for name, s in fns:
    eml_c = s.count("EML")
    total_symb = 2 * eml_c + 1 if eml_c > 0 else 1
    dag_root = parse_to_dag(s)
    unique_set = set()
    dag_root.collect(unique_set)
    unique_c = len(unique_set)
    ratio = f"{total_symb / unique_c:.1f}x" if unique_c > 0 else "1.0x"
    print(f"{name:<12} | {eml_c:<18} | {total_symb:<18} | {unique_c:<20} | {ratio:<15} | {len(s)}")
print("=" * 115)
