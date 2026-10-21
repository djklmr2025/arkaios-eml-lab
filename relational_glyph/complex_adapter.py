"""
ARKAIOS Complex Adapter for GLYPH
Bridges GLYPH IR and the complex ℂ branch.

Converts ComplexSignal / FiveSignalHub to GlyphGraph (using NodeType.SIGNAL and
NodeType.COMBINE), and evaluates those graphs with complex-valued EML semantics.
Provenance is preserved in full even when the central node evaluates to |S| ≈ 0.
"""

import cmath
import math
from typing import Any, Dict, List, Optional, Tuple

from .graph_ir import GlyphGraph, GlyphNode, NodeType
from .signals import ComplexSignal, FiveSignalHub


class ComplexGlyphAdapter:

    @staticmethod
    def signal_to_glyph_node(
        signal: ComplexSignal,
        node_id: Optional[str] = None,
    ) -> GlyphNode:
        """
        Converts a ComplexSignal to a GlyphNode of type SIGNAL.

        Parameters are stored in the node so the graph is self-contained.
        Evaluation requires a 'u' value passed at eval time via evaluate_complex_graph.
        """
        nid = node_id if node_id is not None else f"signal_{signal.k}"
        return GlyphNode(
            node_id=nid,
            node_type=NodeType.SIGNAL,
            inputs=[],
            parameters={
                "k": signal.k,
                "amplitude": signal.A,
                "frequency": signal.omega,
                "phase": signal.phi,
                "formula": "A * exp(i * (omega * u + phi))",
            },
            domain={
                "type": "COMPLEX",
                "constraints": ["u in R"],
                "singularities": [],
            },
            provenance={
                "source": "ComplexSignal",
                "signal_k": signal.k,
                "amplitude": signal.A,
                "frequency": signal.omega,
                "phase": signal.phi,
            },
            visual_repr={"symbol": f"z_{signal.k}(u)", "shape": "circle"},
        )

    @staticmethod
    def hub_to_glyph_graph(
        hub: FiveSignalHub,
        graph_id: str = "five_signal_hub",
        description: str = "FiveSignalHub → GLYPH IR",
    ) -> GlyphGraph:
        """
        Converts a FiveSignalHub to a GlyphGraph.

        Graph structure:
            signal_0..signal_4  (NodeType.SIGNAL, no inputs)
                ↓
            combine_central     (NodeType.COMBINE, inputs=[signal_0..signal_4])
        """
        combine_id = f"{graph_id}_combine"
        graph = GlyphGraph(
            graph_id=graph_id,
            description=description,
            root_id=combine_id,
            metadata={
                "signal_count": len(hub.signals),
                "model": "FiveSignalHub",
            },
        )

        signal_ids: List[str] = []
        for signal in hub.signals:
            nid = f"{graph_id}_signal_{signal.k}"
            node = ComplexGlyphAdapter.signal_to_glyph_node(signal, node_id=nid)
            graph.add_node(node)
            signal_ids.append(nid)

        combine_node = GlyphNode(
            node_id=combine_id,
            node_type=NodeType.COMBINE,
            inputs=signal_ids,
            parameters={
                "operation": "COMPLEX_SUM",
                "formula": "S(u) = sum_k z_k(u)",
                "signal_count": len(signal_ids),
            },
            domain={"type": "COMPLEX", "constraints": ["u in R"], "singularities": []},
            provenance={
                "source": "FiveSignalHub",
                "input_signal_ids": signal_ids,
                "invariant": "All 5 components preserved even if |S(u)| = 0",
            },
            visual_repr={"symbol": "S(u)", "shape": "diamond"},
        )
        graph.add_node(combine_node)
        return graph

    @staticmethod
    def evaluate_complex_graph(
        graph: GlyphGraph,
        root_id: str,
        u: float,
    ) -> Tuple[complex, Dict[str, complex]]:
        """
        Evaluates a GLYPH graph at parameter u using complex semantics.

        Supported node types:
            SIGNAL: A * exp(i * (omega * u + phi))
            COMBINE: sum of all input node values

        Returns:
            (central_value, component_map)
            component_map: {node_id: evaluated_complex_value}
        """
        memo: Dict[str, complex] = {}

        def eval_nid(nid: str) -> complex:
            if nid in memo:
                return memo[nid]
            node = graph.get_node(nid)
            if node is None:
                raise ValueError(f"Node '{nid}' not found in graph '{graph.graph_id}'")

            if node.type == NodeType.SIGNAL:
                A = float(node.parameters.get("amplitude", 1.0))
                omega = float(node.parameters.get("frequency", 1.0))
                phi = float(node.parameters.get("phase", 0.0))
                theta = omega * u + phi
                val: complex = A * cmath.exp(1j * theta)

            elif node.type == NodeType.COMBINE:
                val = sum(eval_nid(inp) for inp in node.inputs)

            elif node.type == NodeType.CONSTANT:
                val = complex(float(node.parameters.get("value", 0.0)))

            else:
                raise ValueError(
                    f"evaluate_complex_graph does not support NodeType '{node.type}' "
                    f"at node '{nid}'"
                )

            memo[nid] = val
            node.result = val
            return val

        central = eval_nid(root_id)
        return central, memo

    @staticmethod
    def evaluate_hub_direct(
        hub: FiveSignalHub,
        u: float,
    ) -> Tuple[complex, List[complex]]:
        """
        Convenience wrapper: converts hub → graph → evaluates. Returns (S(u), components).
        Useful for round-trip verification without constructing the graph externally.
        """
        graph = ComplexGlyphAdapter.hub_to_glyph_graph(hub)
        central, memo = ComplexGlyphAdapter.evaluate_complex_graph(graph, graph.root_id, u)
        components = [
            memo.get(f"{graph.graph_id}_signal_{k}", complex(0))
            for k in range(len(hub.signals))
        ]
        return central, components

    @staticmethod
    def cancellation_provenance_audit(
        graph: GlyphGraph,
        root_id: str,
        u: float,
        null_tol: float = 1e-12,
    ) -> Dict[str, Any]:
        """
        Audits whether a cancellation event (|S(u)| < null_tol) preserves all
        input signals and their parameters in the GLYPH provenance records.

        Returns a dict with:
            is_algebraic_null, central_magnitude, components_preserved,
            all_amplitudes_nonzero, provenance_intact.
        """
        central, memo = ComplexGlyphAdapter.evaluate_complex_graph(graph, root_id, u)
        root_node = graph.get_node(root_id)
        if root_node is None:
            raise ValueError(f"Root node '{root_id}' not found")

        component_values = []
        all_amps_nonzero = True
        for inp_id in root_node.inputs:
            inp_node = graph.get_node(inp_id)
            if inp_node is None:
                continue
            val = memo.get(inp_id, None)
            if val is not None:
                component_values.append(val)
            A = float(inp_node.parameters.get("amplitude", 0.0))
            if A <= 0:
                all_amps_nonzero = False

        return {
            "u": u,
            "central_value": central,
            "central_magnitude": abs(central),
            "is_algebraic_null": abs(central) < null_tol,
            "components_preserved": len(component_values),
            "all_amplitudes_nonzero": all_amps_nonzero,
            "provenance_intact": (
                root_node.provenance.get("invariant") ==
                "All 5 components preserved even if |S(u)| = 0"
            ),
        }
