"""
ARKAIOS Provenance Module for Relational Core and GLYPH
Provides immutable causal tracking, cryptographic hashing, and complete ancestry reconstruction.

Invariant:
A null result (e.g., cancellation to 0) does not destroy inputs, parameters, or provenance.
"""

import hashlib
import json
import time
from typing import Any, Dict, List, Optional


class ProvenanceRecord:
    def __init__(
        self,
        trace_id: str,
        operation: str,
        relation: str,
        inputs: List[Any],
        result: Any,
        causal_parents: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[float] = None,
    ):
        self.trace_id = trace_id
        self.operation = operation
        self.relation = relation
        self.inputs = inputs
        self.result = result
        self.causal_parents = causal_parents or []
        self.metadata = metadata or {}
        self.timestamp = timestamp or time.time()
        self.hash = self._compute_hash()

    def _compute_hash(self) -> str:
        payload = {
            "trace_id": self.trace_id,
            "operation": self.operation,
            "relation": self.relation,
            "inputs": [str(x) for x in self.inputs],
            "result": str(self.result),
            "causal_parents": self.causal_parents,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "operation": self.operation,
            "relation": self.relation,
            "inputs": self.inputs,
            "result": self.result,
            "causal_parents": self.causal_parents,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
            "hash": self.hash,
        }

    def __repr__(self) -> str:
        return f"<ProvenanceRecord {self.trace_id}: op={self.operation}, rel={self.relation}, res={self.result}>"


class ProvenanceStore:
    def __init__(self):
        self._records: Dict[str, ProvenanceRecord] = {}

    def record(
        self,
        trace_id: str,
        operation: str,
        relation: str,
        inputs: List[Any],
        result: Any,
        causal_parents: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ProvenanceRecord:
        rec = ProvenanceRecord(
            trace_id=trace_id,
            operation=operation,
            relation=relation,
            inputs=inputs,
            result=result,
            causal_parents=causal_parents,
            metadata=metadata,
        )
        self._records[trace_id] = rec
        return rec

    def get(self, trace_id: str) -> Optional[ProvenanceRecord]:
        return self._records.get(trace_id)

    def trace_ancestry(self, trace_id: str) -> List[ProvenanceRecord]:
        """Returns the full causal ancestry chain in topological order (earliest to latest)."""
        visited = set()
        chain: List[ProvenanceRecord] = []

        def dfs(curr_id: str):
            if curr_id in visited or curr_id not in self._records:
                return
            visited.add(curr_id)
            rec = self._records[curr_id]
            for parent_id in rec.causal_parents:
                dfs(parent_id)
            chain.append(rec)

        dfs(trace_id)
        return chain

    def all_records(self) -> List[ProvenanceRecord]:
        return list(self._records.values())

    def clear(self):
        self._records.clear()
