"""
ARKAIOS Relational Core Module
Implements the 5 core relational capabilities:
- COMBINE: Aggregation of independent inputs.
- REINFORCE: Constructive reinforcement of compatible contributions.
- CANCEL: Destructive cancellation of opposite contributions without data loss.
- TRANSFORM: Algebraic and symbolic mapping according to verified rules.
- TRACE: Provenance query and complete causal lineage reconstruction.

Mandatory Invariant:
A null result (e.g. combine([5, -5]) -> 0) does not destroy inputs, parameters, or provenance.
"""

import uuid
from typing import Any, Callable, Dict, List, Optional

from .graph_ir import GlyphGraph, GlyphNode, NodeType
from .provenance import ProvenanceRecord, ProvenanceStore


class RelationalResult:
    def __init__(
        self,
        result_id: str,
        value: Any,
        operation: str,
        relation: str,
        inputs: List[Any],
        trace_id: str,
        is_null: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.result_id = result_id
        self.value = value
        self.operation = operation
        self.relation = relation
        self.inputs = inputs
        self.trace_id = trace_id
        self.is_null = is_null
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "result_id": self.result_id,
            "value": self.value,
            "operation": self.operation,
            "relation": self.relation,
            "inputs": self.inputs,
            "trace_id": self.trace_id,
            "is_null": self.is_null,
            "metadata": self.metadata,
        }

    def __repr__(self) -> str:
        return f"<RelationalResult id={self.result_id} val={self.value} op={self.operation} rel={self.relation}>"


class RelationalCore:
    def __init__(self, provenance_store: Optional[ProvenanceStore] = None):
        self.provenance = provenance_store or ProvenanceStore()
        self.graph = GlyphGraph(graph_id=f"relational_core_{uuid.uuid4().hex[:8]}")
        self._results: Dict[str, RelationalResult] = {}

    def combine(
        self,
        inputs: List[Any],
        operation: str = "ADD",
        aggregator: Optional[Callable[[List[Any]], Any]] = None,
    ) -> RelationalResult:
        """
        Combines independent inputs.
        If inputs sum to 0 (e.g., [5, -5]), produces result = 0 with relation = 'CANCELLATION',
        preserving 100% of inputs in the provenance record.
        """
        if aggregator is not None:
            val = aggregator(inputs)
        elif operation == "ADD":
            val = sum(inputs)
        elif operation == "MULTIPLY":
            val = 1
            for x in inputs:
                val *= x
        else:
            val = inputs

        is_null = False
        try:
            if abs(val) < 1e-12:
                is_null = True
        except TypeError:
            is_null = (val == 0 or val == [] or val == "")

        relation = "CANCELLATION" if is_null else "COMBINATION"
        trace_id = f"trace_{uuid.uuid4().hex[:10]}"
        result_id = f"res_{uuid.uuid4().hex[:8]}"

        self.provenance.record(
            trace_id=trace_id,
            operation=operation,
            relation=relation,
            inputs=inputs,
            result=val,
            metadata={"is_null": is_null, "result_id": result_id},
        )

        res = RelationalResult(
            result_id=result_id,
            value=val,
            operation=operation,
            relation=relation,
            inputs=inputs,
            trace_id=trace_id,
            is_null=is_null,
        )
        self._results[result_id] = res

        # Register in internal graph IR
        self.graph.add_node(
            GlyphNode(
                node_id=result_id,
                node_type=NodeType.COMBINE,
                inputs=[],
                parameters={"operation": operation, "relation": relation},
                result=val,
                provenance={"trace_id": trace_id},
            )
        )

        return res

    def reinforce(
        self,
        inputs: List[Any],
        factor: float = 1.0,
        relation: str = "REINFORCEMENT",
    ) -> RelationalResult:
        """Reinforces compatible contributions."""
        combined_val = sum(inputs) * factor
        trace_id = f"trace_{uuid.uuid4().hex[:10]}"
        result_id = f"res_{uuid.uuid4().hex[:8]}"

        self.provenance.record(
            trace_id=trace_id,
            operation="REINFORCE",
            relation=relation,
            inputs=inputs,
            result=combined_val,
            metadata={"factor": factor, "result_id": result_id},
        )

        res = RelationalResult(
            result_id=result_id,
            value=combined_val,
            operation="REINFORCE",
            relation=relation,
            inputs=inputs,
            trace_id=trace_id,
            is_null=(abs(combined_val) < 1e-12 if isinstance(combined_val, (int, float, complex)) else False),
            metadata={"factor": factor},
        )
        self._results[result_id] = res
        return res

    def cancel(
        self,
        inputs: List[Any],
        relation: str = "DESTRUCTIVE_INTERFERENCE",
    ) -> RelationalResult:
        """
        Explicitly cancels opposing contributions.
        Guarantees that cancellation retains all inputs and provenance.
        """
        val = sum(inputs)
        is_null = abs(val) < 1e-12 if isinstance(val, (int, float, complex)) else (val == 0)
        trace_id = f"trace_{uuid.uuid4().hex[:10]}"
        result_id = f"res_{uuid.uuid4().hex[:8]}"

        self.provenance.record(
            trace_id=trace_id,
            operation="CANCEL",
            relation=relation,
            inputs=inputs,
            result=val,
            metadata={"is_null": is_null, "result_id": result_id},
        )

        res = RelationalResult(
            result_id=result_id,
            value=val,
            operation="CANCEL",
            relation=relation,
            inputs=inputs,
            trace_id=trace_id,
            is_null=is_null,
        )
        self._results[result_id] = res
        return res

    def transform(
        self,
        expression: Any,
        rule_name: str,
        transform_fn: Callable[[Any], Any],
        precondition: Optional[Callable[[Any], bool]] = None,
    ) -> RelationalResult:
        """Applies verified algebraic/symbolic transformation."""
        if precondition is not None and not precondition(expression):
            raise ValueError(f"Precondition failed for transformation rule '{rule_name}' on {expression}")

        new_val = transform_fn(expression)
        trace_id = f"trace_{uuid.uuid4().hex[:10]}"
        result_id = f"res_{uuid.uuid4().hex[:8]}"

        self.provenance.record(
            trace_id=trace_id,
            operation="TRANSFORM",
            relation=f"RULE:{rule_name}",
            inputs=[expression],
            result=new_val,
            metadata={"rule": rule_name, "result_id": result_id},
        )

        res = RelationalResult(
            result_id=result_id,
            value=new_val,
            operation="TRANSFORM",
            relation=f"RULE:{rule_name}",
            inputs=[expression],
            trace_id=trace_id,
            metadata={"rule": rule_name},
        )
        self._results[result_id] = res
        return res

    def trace(self, result_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves the full provenance record and causal lineage for any result."""
        res = self._results.get(result_id)
        if not res:
            return None
        rec = self.provenance.get(res.trace_id)
        ancestry = self.provenance.trace_ancestry(res.trace_id)
        return {
            "result": res.to_dict(),
            "record": rec.to_dict() if rec else None,
            "ancestry_length": len(ancestry),
            "ancestry_hashes": [a.hash for a in ancestry],
        }

    def process_five_inputs(
        self,
        inputs: List[Any],
        weights: Optional[List[float]] = None,
    ) -> RelationalResult:
        """
        Executes INPUT[0..4] -> RELATIONAL_CORE -> RESULT.
        Preserves references to all 5 inputs and their exact applied transformations.
        """
        if len(inputs) != 5:
            raise ValueError(f"Expected exactly 5 inputs, got {len(inputs)}")

        w = weights or [1.0] * 5
        weighted = [inputs[i] * w[i] for i in range(5)]
        central_val = sum(weighted)

        return self.combine(
            inputs=inputs,
            operation="FIVE_SIGNAL_CONVERGENCE",
            aggregator=lambda x: sum(x[i] * w[i] for i in range(5)),
        )
