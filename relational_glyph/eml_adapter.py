"""
ARKAIOS EML Adapter for GLYPH
Provides bidirectional conversion between EML AST/DAG representations and the ARKAIOS-GLYPH IR.
Reuses existing primitives and generators from eml-lab without rewriting them.
Includes domain analysis and singularity detection.
"""

import sys
import os
from typing import Any, Dict, List, Optional, Set, Tuple

# Ensure eml-lab root is on sys.path for direct import
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from generator import EMLNode, eml_node, get_constant, get_variable
from .graph_ir import GlyphGraph, GlyphNode, NodeType


class EmlGlyphAdapter:
    @staticmethod
    def eml_to_glyph_graph(
        root_eml: EMLNode,
        graph_id: str = "eml_translated_graph",
        description: str = "Translated from EML expression",
    ) -> GlyphGraph:
        """
        Recursively translates an EMLNode DAG into a validated GlyphGraph.
        Preserves node sharing (hash-consing) as DAG edges.
        """
        graph = GlyphGraph(
            graph_id=graph_id,
            description=description,
            root_id=root_eml.key,
        )
        visited: Set[str] = set()

        def convert_node(node: EMLNode):
            if node.key in visited:
                return
            visited.add(node.key)

            if not node.is_op:
                # Leaf node: Constant or Variable
                if isinstance(node.val, (int, float)):
                    node_type = NodeType.CONSTANT
                    domain = {"type": "REAL", "constraints": [f"val == {node.val}"]}
                    params = {"value": float(node.val)}
                else:
                    node_type = NodeType.VARIABLE
                    domain = {"type": "REAL", "constraints": ["x in R"]}
                    params = {"variable_name": str(node.val)}

                glyph_node = GlyphNode(
                    node_id=node.key,
                    node_type=node_type,
                    inputs=[],
                    parameters=params,
                    domain=domain,
                    result=node.val if isinstance(node.val, (int, float)) else None,
                    provenance={"source": "EML_LEAF", "key": node.key},
                    visual_repr={"symbol": str(node.val), "shape": "box"},
                )
            else:
                # EML Operator node: eml(left, right) = exp(left) - ln(right)
                convert_node(node.left)
                convert_node(node.right)

                domain = {
                    "type": "REAL",
                    "constraints": ["left in R", "right > 0"],
                    "singularities": ["right <= 0 (ln undefined)"],
                }
                glyph_node = GlyphNode(
                    node_id=node.key,
                    node_type=NodeType.EML,
                    inputs=[node.left.key, node.right.key],
                    parameters={"operator": "eml", "formula": "exp(left) - ln(right)"},
                    domain=domain,
                    provenance={"source": "EML_OPERATOR", "key": node.key},
                    visual_repr={"symbol": "EML", "shape": "diamond"},
                )

            graph.add_node(glyph_node)

        convert_node(root_eml)
        return graph

    @staticmethod
    def evaluate_glyph_eml(
        graph: GlyphGraph,
        root_id: str,
        env: Dict[str, float],
        mode: str = "stabilized",
    ) -> Tuple[float, Dict[str, int]]:
        """
        Evaluates a GlyphGraph with EML semantics, returning (result_value, op_counter).
        """
        counter = {"exp": 0, "ln": 0}
        memo: Dict[str, float] = {}

        def eval_nid(nid: str) -> float:
            if nid in memo:
                return memo[nid]
            node = graph.get_node(nid)
            if node is None:
                raise ValueError(f"Node id '{nid}' not found in graph")

            if node.type == NodeType.CONSTANT:
                val = float(node.parameters.get("value", 0.0))
            elif node.type == NodeType.VARIABLE:
                var_name = node.parameters.get("variable_name", "")
                if var_name not in env:
                    raise KeyError(f"Variable '{var_name}' not defined in env: {env}")
                val = float(env[var_name])
            elif node.type == NodeType.EML:
                if len(node.inputs) != 2:
                    raise ValueError(f"EML node '{nid}' must have exactly 2 inputs, got {len(node.inputs)}")
                l_val = eval_nid(node.inputs[0])
                r_val = eval_nid(node.inputs[1])

                counter["exp"] += 1
                counter["ln"] += 1

                if mode == "stabilized":
                    import math
                    l_clamp = max(-20.0, min(20.0, float(l_val)))
                    r_floor = max(1e-300, float(r_val))
                    val = math.exp(l_clamp) - math.log(r_floor)
                else:
                    import math
                    if r_val <= 0:
                        raise ValueError(f"Domain violation at node '{nid}': ln({r_val}) <= 0")
                    val = math.exp(l_val) - math.log(r_val)
            else:
                raise ValueError(f"Unsupported node type '{node.type}' for EML evaluation")

            memo[nid] = val
            node.result = val
            return val

        res = eval_nid(root_id)
        return res, counter

    @staticmethod
    def check_singularities(
        graph: GlyphGraph,
        env: Dict[str, float],
    ) -> List[Dict[str, Any]]:
        """
        Audits graph nodes for potential domain violations under a specific evaluation environment.
        """
        warnings: List[Dict[str, Any]] = []
        try:
            for node in graph.all_nodes():
                if node.type == NodeType.EML and len(node.inputs) == 2:
                    right_node = graph.get_node(node.inputs[1])
                    if right_node and right_node.type == NodeType.CONSTANT:
                        val = float(right_node.parameters.get("value", 1.0))
                        if val <= 0:
                            warnings.append({
                                "node_id": node.id,
                                "type": "STRICT_DOMAIN_VIOLATION",
                                "detail": f"Constant right input {val} <= 0 for natural logarithm",
                            })
        except Exception as e:
            warnings.append({"error": str(e)})

        return warnings
