# Original scripts (verbatim, unmodified)

These are the exact scripts used during the first review sessions, kept for audit. They hard-code `/tmp` paths and
are NOT cleaned up; the reproducible package is in `../eml_lab`, `../scripts`.

| script | what it did | notes |
|---|---|---|
| eml.py | first Sub/Add/Neg construction, tree sizes, mpmath tests | Z-based ln |
| f64.py | float64 stress tests of Sub/Add | |
| mul.py | first M and V (K=14,471 / 21,478,743) with arbitrary precision | **did not finish within 300 s** (dps=700/2500 too heavy); counts come from mul_stats.py |
| mul_stats.py | structure counts of the original M and V | |
| mul_eval1.py / mul_eval2.py | arbitrary-precision tests of M and V (original) | |
| mul_f64.py | float64 map of the original M | |
| search.py / targets.py | FIRST enumeration (7 NARROW sample points). Produced false 'global' formulas | logs: search_narrow_n13.log, targets_narrow.log |
| searchW.py / targetsW.py | enumeration with 8 WIDE sample points (reference) | logs: search_wide_n13.log, targets_wide.log |
| opt.py | optimised constructions (paper ln, K=19 Sub/Add) and size statistics | the SUBS/ADDS strings in this file were edited with sed after the narrow run |
| verify.py, fin.py, var.py, stab.py | verification, float64 map of the new M/V, argument orderings, stable evaluator | |

Pickled enumeration tables (tables*.pkl, ~hundreds of MB) are not included; regenerate with `scripts/06_search.py`.
