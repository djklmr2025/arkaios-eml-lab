"""
ARKAIOS-GLYPH Intermediate Representation (IR)
Provides typed DAG graph structures, cycle detection, domain specifications,
and strict decoupling between visual depiction, symbolic structure, and mathematical evaluation.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Set


class NodeType(str, Enum):
    CONSTANT = "CONSTANT"
    VARIABLE = "VARIABLE"
    EML = "EML"
    COMBINE = "COMBINE"
    TRANSFORM = "TRANSFORM"
    SIGNAL = "SIGNAL"
    RESULT = "RESULT"
    PROVENANCE = "PROVENANCE"


class GlyphNode:
    def __init__(
        self,
        node_id: str,
        node_type: NodeType,
        inputs: Optional[List[str]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        domain: Optional[Dict[str, Any]] = None,
        result: Optional[Any] = None,
        provenance: Optional[Dict[str, Any]] = None,
        visual_repr: Optional[Dict[str, Any]] = None,
    ):
        self.id = str(node_id)
        self.type = node_type if isinstance(node_type, NodeType) else NodeType(node_type)
        self.inputs = [str(x) for x in (inputs or [])]
        self.parameters = parameters or {}
        self.domain = domain or {"type": "REAL", "constraints": [], "singularities": []}
        self.result = result
        self.provenance = provenance or {}
        # Decouple visual appearance from mathematical semantics
        self.visual_repr = visual_repr or {
            "symbol": "",
            "shape": "circle",
            "notes": "Non-semantic visual projection"
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "inputs": self.inputs,
            "parameters": self.parameters,
            "domain": self.domain,
            "result": self.result,
            "provenance": self.provenance,
            "visual_repr": self.visual_repr,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GlyphNode":
        return cls(
            node_id=data["id"],
            node_type=NodeType(data["type"]),
            inputs=data.get("inputs", []),
            parameters=data.get("parameters", {}),
            domain=data.get("domain", {}),
            result=data.get("result"),
            provenance=data.get("provenance", {}),
            visual_repr=data.get("visual_repr", {}),
        )

    def __repr__(self) -> str:
        return f"<GlyphNode id={self.id} type={self.type.value} inputs={self.inputs}>"


class GlyphGraph:
    def __init__(
        self,
        graph_id: str,
        version: str = "1.0.0",
        description: str = "",
        root_id: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.graph_id = graph_id
        self.version = version
        self.description = description
        self.root_id = root_id
        self.metadata = metadata or {}
        self._nodes: Dict[str, GlyphNode] = {}

    def add_node(self, node: GlyphNode) -> GlyphNode:
        if node.id in self._nodes:
            raise ValueError(f"Node id '{node.id}' already exists in graph '{self.graph_id}'")
        self._nodes[node.id] = node
        # Check DAG validity after addition
        self.validate_dag()
        return node

    def get_node(self, node_id: str) -> Optional[GlyphNode]:
        return self._nodes.get(str(node_id))

    def node_count(self) -> int:
        return len(self._nodes)

    def all_nodes(self) -> List[GlyphNode]:
        return list(self._nodes.values())

    def validate_dag(self) -> bool:
        """
        Validates that the graph has no directed cycles.
        Raises ValueError if a cycle is detected.
        """
        # Adjacency list: node -> inputs (directed dependencies)
        # 0 = unvisited, 1 = visiting (on current recursion stack), 2 = visited
        state: Dict[str, int] = {nid: 0 for nid in self._nodes}

        def dfs(curr_id: str, path: List[str]):
            state[curr_id] = 1
            node = self._nodes[curr_id]
            for dep_id in node.inputs:
                if dep_id not in self._nodes:
                    # Input reference outside graph or forward ref
                    continue
                if state[dep_id] == 1:
                    cycle = " -> ".join(path + [dep_id])
                    raise ValueError(f"Cycle detected in GlyphGraph '{self.graph_id}': {cycle}")
                if state[dep_id] == 0:
                    dfs(dep_id, path + [dep_id])
            state[curr_id] = 2

        for nid in self._nodes:
            if state[nid] == 0:
                dfs(nid, [nid])

        return True

    def topological_order(self) -> List[GlyphNode]:
        """Returns nodes in topological dependency order (inputs before dependents)."""
        self.validate_dag()
        visited: Set[str] = set()
        order: List[GlyphNode] = []

        def dfs(curr_id: str):
            if curr_id in visited or curr_id not in self._nodes:
                return
            visited.add(curr_id)
            node = self._nodes[curr_id]
            for dep_id in node.inputs:
                dfs(dep_id)
            order.append(node)

        # Start from root or all nodes
        if self.root_id and self.root_id in self._nodes:
            dfs(self.root_id)
        for nid in self._nodes:
            dfs(nid)

        return order

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "graph_id": self.graph_id,
            "description": self.description,
            "root_id": self.root_id,
            "nodes": [n.to_dict() for n in self._nodes.values()],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GlyphGraph":
        graph = cls(
            graph_id=data["graph_id"],
            version=data.get("version", "1.0.0"),
            description=data.get("description", ""),
            root_id=data.get("root_id", ""),
            metadata=data.get("metadata", {}),
        )
        for nd in data.get("nodes", []):
            graph.add_node(GlyphNode.from_dict(nd))
        return graph
