import math
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from relational_glyph.graph_ir import GlyphGraph, GlyphNode, NodeType
from relational_glyph.optimizer import GlyphOptimizer


class TestOptimizer(unittest.TestCase):
    def test_constant_folding(self):
        graph = GlyphGraph(graph_id="g_fold", root_id="eml_node")
        n1 = GlyphNode(node_id="c1", node_type=NodeType.CONSTANT, parameters={"value": 0.0})
        n2 = GlyphNode(node_id="c2", node_type=NodeType.CONSTANT, parameters={"value": 1.0})
        # eml(0, 1) = exp(0) - ln(1) = 1 - 0 = 1.0
        n_eml = GlyphNode(node_id="eml_node", node_type=NodeType.EML, inputs=["c1", "c2"])

        graph.add_node(n1)
        graph.add_node(n2)
        graph.add_node(n_eml)

        optimizer = GlyphOptimizer()
        opt_graph, report = optimizer.optimize_graph(graph)

        # Original graph remains untouched with 3 nodes
        self.assertEqual(graph.node_count(), 3)
        self.assertIn("eml_node", [n.id for n in graph.all_nodes()])

        # Optimized graph folded eml_node into a single constant node of value 1.0
        self.assertEqual(opt_graph.node_count(), 1)
        folded_node = opt_graph.all_nodes()[0]
        self.assertEqual(folded_node.type, NodeType.CONSTANT)
        self.assertAlmostEqual(folded_node.parameters["value"], 1.0)
        self.assertEqual(report["transformations_applied"], 1)

    def test_eml_one_reduction(self):
        graph = GlyphGraph(graph_id="g_one", root_id="eml_x_1")
        n_var = GlyphNode(node_id="v_x", node_type=NodeType.VARIABLE, parameters={"variable_name": "x"})
        n_one = GlyphNode(node_id="c_one", node_type=NodeType.CONSTANT, parameters={"value": 1.0})
        n_eml = GlyphNode(node_id="eml_x_1", node_type=NodeType.EML, inputs=["v_x", "c_one"])

        graph.add_node(n_var)
        graph.add_node(n_one)
        graph.add_node(n_eml)

        optimizer = GlyphOptimizer()
        opt_graph, report = optimizer.optimize_graph(graph)

        target = opt_graph.get_node("eml_x_1")
        self.assertIsNotNone(target)
        self.assertEqual(target.parameters.get("optimized_form"), "exp(x)")
        self.assertIn("EML_ONE_REDUCTION", report["rules_applied"])


if __name__ == "__main__":
    unittest.main()
