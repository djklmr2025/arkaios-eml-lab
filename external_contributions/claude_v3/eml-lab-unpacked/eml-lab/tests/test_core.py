"""Fast regression tests (< 1 minute): python -m unittest discover -s tests -v"""
import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import mpmath as mp
from eml_lab.constructions import CATALOG
from eml_lab.core import describe, rpn, parse_rpn, size
from eml_lab.evaluators import eval_mp, adaptive_eval, DomainError

EXPECTED_K = {'Sub_orig': 31, 'Add_orig': 139, 'M_orig': 14471, 'V_orig': 21478743, 'Sub_pl': 19, 'Add_pl': 91,
              'M_pl': 7547, 'Sub19': 19, 'Add19': 19, 'M_opt': 631, 'V_opt': 88715}
class T(unittest.TestCase):
    def test_counts(self):
        for k, v in EXPECTED_K.items(): self.assertEqual(describe(CATALOG[k][0]())['K'], v, k)
    def test_rpn_roundtrip(self):
        for k in ('Sub19', 'Add19', 'M_opt'):
            node = CATALOG[k][0](); self.assertEqual(size(parse_rpn(rpn(node))), size(node))
    def test_sub_add_domain_and_value(self):
        pts = [-30, -3, -0.25, 0, 0.25, 2.7, 30]
        for k in ('Sub19', 'Add19'):
            node, truth = CATALOG[k][0](), CATALOG[k][1]
            for a in pts:
                for b in pts:
                    v = eval_mp(node, a, b, 200)     # raises DomainError if any ln argument <= 0
                    self.assertLess(abs(v - truth(mp.mpf(a), mp.mpf(b))), mp.mpf(10) ** -150)
    def test_mul_adaptive(self):
        node, truth = CATALOG['M_opt']
        node = node()
        for a, b in [(3, 3), (-2, 0.5), (0, 1), (1, 1), (-3, -3)]:
            v, d, m = adaptive_eval(node, a, b, target_digits=25)
            self.assertLess(abs(v - mp.mpf(a) * b), mp.mpf(10) ** -25)
    def test_mul_3_3_needs_many_digits(self):
        node = CATALOG['M_opt'][0]()
        self.assertGreater(abs(float(eval_mp(node, 3, 3, 50)) - 9.0), 8.0)   # pure EML at 50 digits is garbage (~1e-51), NOT 9
        self.assertAlmostEqual(float(eval_mp(node, 3, 3, 420)), 9.0, places=12)
    def test_div_adaptive(self):
        node = CATALOG['V_opt'][0]()
        for a, b in [(1.5, 2), (-2, 0.5), (1, -1)]:
            v, d, m = adaptive_eval(node, a, b, target_digits=25)
            self.assertLess(abs(v - mp.mpf(a) / b), mp.mpf(10) ** -25)
if __name__ == '__main__': unittest.main()

class TestDivisionV2(unittest.TestCase):
    def test_sizes_and_values(self):
        import mpmath as mp
        from eml_lab.core import X, Y, size
        from eml_lab import division_v2 as d
        from eml_lab.evaluators import eval_mp
        m, v = d.M571(X, Y), d.V_pq(X, Y, (0, 1, 0, 0, 1, 0))
        self.assertEqual((size(m), size(v)), (571, 2987))
        self.assertLess(abs(eval_mp(m, 1.5, -2, 120) - mp.mpf(-3)), mp.mpf(10) ** -60)
        self.assertLess(abs(eval_mp(v, 1.5, -2, 160) - mp.mpf(-0.75)), mp.mpf(10) ** -60)

class TestComplexBranch(unittest.TestCase):
    def test_i_pi_cos(self):
        import mpmath as mp
        from eml_lab.core import X
        from eml_lab import complex_constructions as C
        from eml_lab.complex_eval import ceval
        self.assertLess(abs(ceval(C.I, {'x': 0}, 60) - mp.mpc(0, 1)), mp.mpf(10) ** -50)
        mp.mp.dps = 60; self.assertLess(abs(ceval(C.PI, {'x': 0}, 60) - mp.pi), mp.mpf(10) ** -50)
        node = C.COS2(X)
        for x in (0, 1.5, -2.75):
            v = ceval(node, {'x': mp.mpf(x)}, 70); mp.mp.dps = 70
            self.assertLess(abs(v - mp.cos(x)), mp.mpf(10) ** -50)
