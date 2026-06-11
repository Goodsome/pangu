from dataclasses import dataclass
from dataclasses import field
from typing import Self
from codegen.code_metadata.domain.aggregates.code_node import CodeNode
from codegen.code_metadata.domain.aggregates.code_node import ExternalNode
from codegen.shared.domain.enums import PythonBuiltinType


@dataclass
class NodeRegistry:
    store_by_fqn: dict[str, CodeNode] = field(default_factory=dict)
    temp_store: dict[str, CodeNode] = field(default_factory=dict)
    upsert_nodes: list[CodeNode] = field(default_factory=list)

    @classmethod
    def create(cls, nodes: list[CodeNode]) -> Self:
        return cls(store_by_fqn={node.id: node for node in nodes}, temp_store={})

    @property
    def nodes(self) -> list[CodeNode]:
        return list(self.store_by_fqn.values())

    def get_node(self, fqn: str) -> CodeNode:
        self._ensure_external_node(fqn)
        if fqn in self.store_by_fqn:
            return self.store_by_fqn[fqn]
        if fqn in self.temp_store:
            return self.temp_store[fqn]
        raise ValueError(f"Unknown FQN: {fqn}")

    def find_node(self, fqn: str) -> CodeNode | None:
        return self.store_by_fqn.get(fqn)

    def _ensure_external_node(self, fqn: str) -> None:
        if fqn in self.store_by_fqn:
            return
        if fqn in PythonBuiltinType._value2member_map_:
            node = ExternalNode(id=fqn, name=fqn)
            self.add_node(node)
        elif not fqn.startswith("codegen."):
            node = ExternalNode(id=fqn, name=fqn.split(".")[-1])
            self.add_node(node)

    def add_node(self, node: CodeNode) -> None:
        if node.id in self.store_by_fqn:
            raise ValueError(f"Duplicate: node.fqn={node.id!r}")
        self.store_by_fqn[node.id] = node
        self.upsert_nodes.append(node)

    def add_temp_node(self, dto: CodeNode) -> None:
        self.temp_store[dto.id] = dto

    def registry_nodes(self, nodes: list[CodeNode]) -> None:
        for node in nodes:
            if node.id in self.store_by_fqn:
                continue
            self.store_by_fqn[node.id] = node
