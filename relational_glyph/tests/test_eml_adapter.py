import math
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from generator import get_variable, get_constant, eml_node
from primitives import block_Exp, block_L, block_P
from relational_glyph.eml_adapter import EmlGlyphAdapter


class TestEmlAdapter(unittest.TestCase):
    def test_exp_adapter_translation_and_eval(self):
        # Exp(x) = eml(x, 1) = exp(x)
        x_var = get_variable("x")
        exp_node = block_Exp(x_var)

        graph = EmlGlyphAdapter.eml_to_glyph_graph(exp_node)
        self.assertGreater(graph.node_count(), 0)
        self.assertTrue(graph.validate_dag())

        env = {"x": 2.0}
        val, counter = EmlGlyphAdapter.evaluate_glyph_eml(graph, graph.root_id, env)
        expected = math.exp(2.0)
        self.assertAlmostEqual(val, expected, places=7)
        self.assertGreaterEqual(counter["exp"], 1)

    def test_block_p_translation(self):
        # P(a, b) = a - b
        a_var = get_variable("a")
        b_var = get_variable("b")
        sub_node = block_P(a_var, b_var)

        graph = EmlGlyphAdapter.eml_to_glyph_graph(sub_node)
        self.assertTrue(graph.validate_dag())

        env = {"a": 7.5, "b": 2.5}
        val, _ = EmlGlyphAdapter.evaluate_glyph_eml(graph, graph.root_id, env)
        # In stabilized mode P(7.5, 2.5) evaluates close to 5.0
        self.assertTrue(abs(val - 5.0) < 1e-4)

    def test_singularity_detection(self):
        # eml(1, -5): right argument is -5 <= 0
        c_left = get_constant(1.0)
        c_right = get_constant(-5.0)
        bad_node = eml_node(c_left, c_right)

        graph = EmlGlyphAdapter.eml_to_glyph_graph(bad_node)
        warnings = EmlGlyphAdapter.check_singularities(graph, env={})
        self.assertGreaterEqual(len(warnings), 1)
        self.assertEqual(warnings[0]["type"], "STRICT_DOMAIN_VIOLATION")


if __name__ == "__main__":
    unittest.main()
