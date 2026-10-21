"""
ARKAIOS Symbolic Optimizer for GLYPH & EML Graphs
Implements verified transformation rules with explicit preconditions, algebraic proofs,
domain boundaries, and equivalence testing.

Mandatory Invariant:
Preserves both the original graph and the optimized graph for auditability.
"""

import copy
import math
from typing import Any, Callable, Dict, List, Optional, Tuple

from .graph_ir import GlyphGraph, GlyphNode, NodeType


class OptimizationRule:
    def __init__(
        self,
        name: str,
        description: str,
        justification: str,
        domain_bounds: Dict[str, Any],
        precondition: Callable[[GlyphNode, GlyphGraph], bool],
        transform: Callable[[GlyphNode, GlyphGraph], Optional[GlyphNode]],
    ):
        self.name = name
        self.description = description
        self.justification = justification
        self.domain_bounds = domain_bounds
        self.precondition = precondition
        self.transform = transform

    def verify_equivalence(
        self,
        test_inputs: List[float],
        eval_orig_fn: Callable[[float], float],
        eval_opt_fn: Callable[[float], float],
        tol: float = 1e-12,
    ) -> bool:
        """Numerically validates equivalence over test sample inputs."""
        for x in test_inputs:
            v_orig = eval_orig_fn(x)
            v_opt = eval_opt_fn(x)
            if abs(v_orig - v_opt) > tol:
                return False
        return True


class GlyphOptimizer:
    def __init__(self):
        self.rules: List[OptimizationRule] = []
        self._register_default_rules()

    def _register_default_rules(self):
        # Rule 1: Constant Folding
        def pre_const_fold(node: GlyphNode, graph: GlyphGraph) -> bool:
            if node.type == NodeType.EML and len(node.inputs) == 2:
                n1 = graph.get_node(node.inputs[0])
                n2 = graph.get_node(node.inputs[1])
                return (
                    n1 is not None and n1.type == NodeType.CONSTANT
                    and n2 is not None and n2.type == NodeType.CONSTANT
                    and float(n2.parameters.get("value", 1.0)) > 0
                )
            return False

        def trans_const_fold(node: GlyphNode, graph: GlyphGraph) -> Optional[GlyphNode]:
            n1 = graph.get_node(node.inputs[0])
            n2 = graph.get_node(node.inputs[1])
            v1 = float(n1.parameters["value"])
            v2 = float(n2.parameters["value"])
            # Fold: exp(v1) - ln(v2)
            try:
                res = math.exp(v1) - math.log(v2)
                folded_id = f"const_{node.id}"
                return GlyphNode(
                    node_id=folded_id,
                    node_type=NodeType.CONSTANT,
                    inputs=[],
                    parameters={"value": res},
                    domain={"type": "REAL", "constraints": [f"val == {res}"]},
                    result=res,
                    provenance={"rule": "CONSTANT_FOLDING", "original_id": node.id},
                )
            except (OverflowError, ValueError):
                return None

        self.rules.append(
            OptimizationRule(
                name="CONSTANT_FOLDING",
                description="Folds EML nodes with purely constant real inputs.",
                justification="eml(c1, c2) = exp(c1) - ln(c2) evaluates to a deterministic real constant for c2 > 0.",
                domain_bounds={"left": "finite R", "right": "> 0"},
                precondition=pre_const_fold,
                transform=trans_const_fold,
            )
        )

        # Rule 2: EML(x, 1) -> Exp(x)
        def pre_eml_one(node: GlyphNode, graph: GlyphGraph) -> bool:
            if node.type == NodeType.EML and len(node.inputs) == 2:
                r_node = graph.get_node(node.inputs[1])
                if r_node and r_node.type == NodeType.CONSTANT:
                    return abs(float(r_node.parameters.get("value", 0.0)) - 1.0) < 1e-15
            return False

        def trans_eml_one(node: GlyphNode, graph: GlyphGraph) -> Optional[GlyphNode]:
            # eml(x, 1) = exp(x) - ln(1) = exp(x) - 0 = exp(x)
            node.parameters["optimized_form"] = "exp(x)"
            node.parameters["subtracted_ln1"] = 0.0
            return node

        self.rules.append(
            OptimizationRule(
                name="EML_ONE_REDUCTION",
                description="Simplifies eml(x, 1) -> exp(x).",
                justification="ln(1) = 0, so exp(x) - ln(1) = exp(x).",
                domain_bounds={"x": "R"},
                precondition=pre_eml_one,
                transform=trans_eml_one,
            )
        )

    def optimize_graph(
        self,
        graph: GlyphGraph,
        max_passes: int = 5,
    ) -> Tuple[GlyphGraph, Dict[str, Any]]:
        """
        Applies optimization rules, producing a new optimized GlyphGraph
        while strictly preserving the original.
        """
        # Deepcopy to keep original graph intact
        opt_graph = GlyphGraph.from_dict(graph.to_dict())
        opt_graph.graph_id = f"{graph.graph_id}_optimized"

        transform_count = 0
        rules_applied: List[str] = []

        for _ in range(max_passes):
            changed = False
            for node in list(opt_graph.all_nodes()):
                for rule in self.rules:
                    if rule.precondition(node, opt_graph):
                        new_node = rule.transform(node, opt_graph)
                        if new_node is not None and new_node.id != node.id:
                            # Replace references in other nodes
                            for other in opt_graph.all_nodes():
                                other.inputs = [
                                    new_node.id if inp == node.id else inp
                                    for inp in other.inputs
                                ]
                            if opt_graph.root_id == node.id:
                                opt_graph.root_id = new_node.id
                            opt_graph._nodes[new_node.id] = new_node
                            del opt_graph._nodes[node.id]
                            changed = True
                            transform_count += 1
                            rules_applied.append(rule.name)
                            break
                        elif new_node is not None:
                            # Node mutated in-place
                            changed = True
                            transform_count += 1
                            rules_applied.append(rule.name)
                            break
            if not changed:
                break

        # Dead Code Elimination (DCE): prune unreachable orphan nodes from root_id
        if opt_graph.root_id and opt_graph.root_id in opt_graph._nodes:
            reachable = set()
            def mark_reachable(nid: str):
                if nid in reachable or nid not in opt_graph._nodes:
                    return
                reachable.add(nid)
                for dep in opt_graph._nodes[nid].inputs:
                    mark_reachable(dep)
            mark_reachable(opt_graph.root_id)
            for nid in list(opt_graph._nodes.keys()):
                if nid not in reachable:
                    del opt_graph._nodes[nid]

        report = {
            "original_nodes": graph.node_count(),
            "optimized_nodes": opt_graph.node_count(),
            "nodes_reduced": graph.node_count() - opt_graph.node_count(),
            "transformations_applied": transform_count,
            "rules_applied": rules_applied,
        }
        return opt_graph, report
