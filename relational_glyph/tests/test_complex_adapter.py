import cmath
import math
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from relational_glyph.signals import ComplexSignal, FiveSignalHub
from relational_glyph.complex_adapter import ComplexGlyphAdapter
from relational_glyph.graph_ir import GlyphGraph, NodeType


class TestComplexGlyphAdapter(unittest.TestCase):

    # ------------------------------------------------------------------
    # Single signal conversion
    # ------------------------------------------------------------------

    def test_signal_to_glyph_node_structure(self):
        """signal_to_glyph_node produces a SIGNAL node with correct parameters."""
        sig = ComplexSignal(k=2, amplitude=1.5, frequency=2.0, phase=0.3)
        node = ComplexGlyphAdapter.signal_to_glyph_node(sig)

        self.assertEqual(node.type, NodeType.SIGNAL)
        self.assertEqual(node.parameters["k"], 2)
        self.assertAlmostEqual(node.parameters["amplitude"], 1.5)
        self.assertAlmostEqual(node.parameters["frequency"], 2.0)
        self.assertAlmostEqual(node.parameters["phase"], 0.3)
        self.assertEqual(node.inputs, [])

    def test_signal_to_glyph_node_custom_id(self):
        """Custom node_id is respected."""
        sig = ComplexSignal(k=0)
        node = ComplexGlyphAdapter.signal_to_glyph_node(sig, node_id="my_signal_0")
        self.assertEqual(node.id, "my_signal_0")

    # ------------------------------------------------------------------
    # Hub → GlyphGraph conversion
    # ------------------------------------------------------------------

    def test_hub_to_glyph_graph_dag_valid(self):
        """hub_to_glyph_graph produces a valid DAG."""
        hub = FiveSignalHub.create_case_a_reinforce()
        graph = ComplexGlyphAdapter.hub_to_glyph_graph(hub)

        self.assertTrue(graph.validate_dag())
        # 5 SIGNAL nodes + 1 COMBINE node
        self.assertEqual(graph.node_count(), 6)

    def test_hub_to_glyph_graph_root_is_combine(self):
        """Root node is of type COMBINE and references all 5 signals."""
        hub = FiveSignalHub.create_case_a_reinforce()
        graph = ComplexGlyphAdapter.hub_to_glyph_graph(hub)

        root = graph.get_node(graph.root_id)
        self.assertIsNotNone(root)
        self.assertEqual(root.type, NodeType.COMBINE)
        self.assertEqual(len(root.inputs), 5)

    def test_hub_to_glyph_graph_topological_order(self):
        """Topological order: SIGNAL nodes come before COMBINE."""
        hub = FiveSignalHub.create_case_a_reinforce()
        graph = ComplexGlyphAdapter.hub_to_glyph_graph(hub)

        order = graph.topological_order()
        types = [n.type for n in order]
        combine_idx = next(i for i, t in enumerate(types) if t == NodeType.COMBINE)
        for i in range(combine_idx):
            self.assertEqual(types[i], NodeType.SIGNAL)

    # ------------------------------------------------------------------
    # Complex evaluation – Case A (Reinforcement)
    # ------------------------------------------------------------------

    def test_case_a_reinforcement_via_graph(self):
        """Case A: 5 identical unit signals -> |S(u)| = 5 via GLYPH evaluation."""
        hub = FiveSignalHub.create_case_a_reinforce(A=1.0, omega=2.0, phi=0.5)
        graph = ComplexGlyphAdapter.hub_to_glyph_graph(hub)

        for u in [0.0, 1.0, math.pi, 10.0]:
            central, _ = ComplexGlyphAdapter.evaluate_complex_graph(graph, graph.root_id, u)
            self.assertAlmostEqual(
                abs(central), 5.0, places=12,
                msg=f"Reinforcement failed at u={u}: |S| = {abs(central)}"
            )

    def test_case_a_matches_direct_hub_evaluation(self):
        """GLYPH evaluation matches FiveSignalHub.evaluate_central() directly."""
        hub = FiveSignalHub.create_case_a_reinforce(A=2.0, omega=1.5, phi=0.1)
        graph = ComplexGlyphAdapter.hub_to_glyph_graph(hub)
        u = 3.7

        glyph_val, _ = ComplexGlyphAdapter.evaluate_complex_graph(graph, graph.root_id, u)
        direct_val = hub.evaluate_central(u)

        self.assertAlmostEqual(glyph_val.real, direct_val.real, places=12)
        self.assertAlmostEqual(glyph_val.imag, direct_val.imag, places=12)

    # ------------------------------------------------------------------
    # Complex evaluation – Case B (Cancellation)
    # ------------------------------------------------------------------

    def test_case_b_cancellation_via_graph(self):
        """Case B: Symmetric phases phi_k = 2*pi*k/5 -> |S(u)| < 1e-14 via GLYPH."""
        hub = FiveSignalHub.create_case_b_cancel(A=1.0, omega=1.0)
        graph = ComplexGlyphAdapter.hub_to_glyph_graph(hub)

        for u in [0.0, 0.5, 2.0, 7.7]:
            central, _ = ComplexGlyphAdapter.evaluate_complex_graph(graph, graph.root_id, u)
            self.assertLess(
                abs(central), 1e-14,
                msg=f"Cancellation failed at u={u}: |S| = {abs(central)}"
            )

    # ------------------------------------------------------------------
    # Provenance preservation under cancellation
    # ------------------------------------------------------------------

    def test_cancellation_provenance_preserved(self):
        """Cancellation audit: all 5 components and provenance survive |S(u)| ≈ 0."""
        hub = FiveSignalHub.create_case_b_cancel(A=1.0, omega=1.0)
        graph = ComplexGlyphAdapter.hub_to_glyph_graph(hub)

        audit = ComplexGlyphAdapter.cancellation_provenance_audit(
            graph, graph.root_id, u=1.234
        )

        self.assertTrue(audit["is_algebraic_null"])
        self.assertEqual(audit["components_preserved"], 5)
        self.assertTrue(audit["all_amplitudes_nonzero"])
        self.assertTrue(audit["provenance_intact"])

    # ------------------------------------------------------------------
    # Round-trip via evaluate_hub_direct
    # ------------------------------------------------------------------

    def test_evaluate_hub_direct_round_trip(self):
        """evaluate_hub_direct round-trip matches hub direct evaluation."""
        configs = [
            {"amplitude": 1.5, "frequency": 1.0, "phase": 0.0},
            {"amplitude": 2.0, "frequency": 2.5, "phase": 0.4},
            {"amplitude": 0.8, "frequency": 0.5, "phase": 1.2},
            {"amplitude": 1.2, "frequency": 3.0, "phase": 2.1},
            {"amplitude": 2.5, "frequency": 1.8, "phase": 0.7},
        ]
        hub = FiveSignalHub.create_case_c_general(configs)
        u = 2.5

        glyph_central, glyph_components = ComplexGlyphAdapter.evaluate_hub_direct(hub, u)
        direct_central = hub.evaluate_central(u)
        direct_components = hub.evaluate_components(u)

        self.assertAlmostEqual(glyph_central.real, direct_central.real, places=12)
        self.assertAlmostEqual(glyph_central.imag, direct_central.imag, places=12)
        for k in range(5):
            self.assertAlmostEqual(
                glyph_components[k].real, direct_components[k].real, places=12,
                msg=f"Component {k} real mismatch"
            )

    # ------------------------------------------------------------------
    # Unsupported node type guard
    # ------------------------------------------------------------------

    def test_unsupported_node_type_raises(self):
        """evaluate_complex_graph raises ValueError for unsupported node types."""
        from relational_glyph.graph_ir import GlyphNode

        graph = GlyphGraph(graph_id="test_unsupported", root_id="bad_node")
        bad_node = GlyphNode(
            node_id="bad_node",
            node_type=NodeType.EML,
            inputs=[],
            parameters={},
        )
        graph.add_node(bad_node)

        with self.assertRaises(ValueError):
            ComplexGlyphAdapter.evaluate_complex_graph(graph, "bad_node", u=0.0)


if __name__ == "__main__":
    unittest.main()
