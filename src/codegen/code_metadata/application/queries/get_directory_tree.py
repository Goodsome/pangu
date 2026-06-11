from dataclasses import dataclass
from codegen.code_metadata.domain.aggregates.code_node import CodeNode
from codegen.code_metadata.application.dtos.node_tree import NodeTree
from codegen.code_metadata.application.ports.code_node_query_service import (
    CodeNodeQueryService,
)
from codegen.code_metadata.domain.enums.edge_type import EdgeType


@dataclass
class GetDirectoryTree:
    """按 fqn_prefix 查询目录树：从 CodeNodeQueryService 获取平铺 DTO，组装为 NodeTree。"""

    query_service: CodeNodeQueryService

    def execute(self, fqn_prefix: str) -> NodeTree:
        dtos = self.query_service.find_by_fqn_prefix(fqn_prefix)
        index = {d.id: d for d in dtos}
        root_dto = index.get(fqn_prefix)
        if root_dto is None:
            raise ValueError(f"Node with fqn '{fqn_prefix}' not found")
        return self._build_subtree(root_dto, index)

    def _build_subtree(self, dto: CodeNode, index: dict[str, CodeNode]) -> NodeTree:
        children = [
            self._build_subtree(index[e.fqn], index)
            for e in dto.outbound_edges
            if e.kind == EdgeType.DEFINES and e.fqn in index
        ]
        return NodeTree(node=dto, children=children)
