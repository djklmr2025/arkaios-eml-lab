import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from relational_glyph.graph_ir import GlyphGraph, GlyphNode, NodeType


class TestGraphIR(unittest.TestCase):
    def test_valid_dag_creation(self):
        graph = GlyphGraph(graph_id="g1", root_id="node_res")

        n_c1 = GlyphNode(node_id="c1", node_type=NodeType.CONSTANT, parameters={"value": 1.0})
        n_c2 = GlyphNode(node_id="c2", node_type=NodeType.CONSTANT, parameters={"value": 2.0})
        n_eml = GlyphNode(node_id="node_res", node_type=NodeType.EML, inputs=["c1", "c2"])

        graph.add_node(n_c1)
        graph.add_node(n_c2)
        graph.add_node(n_eml)

        self.assertEqual(graph.node_count(), 3)
        self.assertTrue(graph.validate_dag())
        topological = graph.topological_order()
        self.assertEqual(len(topological), 3)
        # c1 and c2 must precede node_res
        ids = [n.id for n in topological]
        self.assertLess(ids.index("c1"), ids.index("node_res"))
        self.assertLess(ids.index("c2"), ids.index("node_res"))

    def test_cycle_rejection(self):
        graph = GlyphGraph(graph_id="g_cycle")
        n1 = GlyphNode(node_id="n1", node_type=NodeType.TRANSFORM, inputs=["n2"])
        n2 = GlyphNode(node_id="n2", node_type=NodeType.TRANSFORM, inputs=["n1"])

        graph.add_node(n1)
        # Adding n2 completes the cycle n1 -> n2 -> n1, so add_node must reject it
        with self.assertRaises(ValueError):
            graph.add_node(n2)

    def test_serialization_round_trip(self):
        graph = GlyphGraph(graph_id="g_serial", root_id="r1")
        n1 = GlyphNode(
            node_id="r1",
            node_type=NodeType.RESULT,
            inputs=[],
            parameters={"val": 42},
            visual_repr={"symbol": "Ω", "shape": "hexagon"},
        )
        graph.add_node(n1)

        data = graph.to_dict()
        self.assertEqual(data["graph_id"], "g_serial")
        self.assertEqual(len(data["nodes"]), 1)

        restored = GlyphGraph.from_dict(data)
        self.assertEqual(restored.graph_id, "g_serial")
        self.assertEqual(restored.node_count(), 1)
        r_node = restored.get_node("r1")
        self.assertIsNotNone(r_node)
        self.assertEqual(r_node.visual_repr["symbol"], "Ω")


if __name__ == "__main__":
    unittest.main()
