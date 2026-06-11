from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
from codegen.code_metadata.application.dtos.code_node_detail_dto import (
    CodeNodeDetailDto,
)
from codegen.code_metadata.domain.aggregates.code_node import ClassNode
from codegen.code_metadata.domain.aggregates.code_node import CodeNode
from codegen.code_metadata.domain.aggregates.code_node import DirectoryNode
from codegen.code_metadata.domain.aggregates.code_node import ExternalNode
from codegen.code_metadata.domain.aggregates.code_node import FileNode
from codegen.code_metadata.domain.aggregates.code_node import FunctionNode
from codegen.code_metadata.domain.aggregates.code_node import MethodNode
from codegen.code_metadata.domain.aggregates.code_node import ModuleNode
from codegen.code_metadata.domain.aggregates.code_node import VariableNode
from codegen.code_metadata.application.dtos.graph_view import GraphViewDTO
from codegen.code_metadata.application.dtos.graph_view import GraphViewNode
from codegen.code_metadata.application.dtos.trace_query import (
    TraceSymbolDependenciesQuery,
)
from codegen.code_metadata.application.ports.code_node_query_service import (
    CodeNodeQueryService,
)
from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind
from codegen.code_metadata.domain.enums.edge_type import EdgeType
from codegen.code_metadata.domain.enums.edge_direction import EdgeDirection


@dataclass
class TraceSymbolDependenciesQueryHandler:
    """CQRS 查询执行器：以 DFS 方式追踪符号的上下游依赖关系。"""

    query_service: CodeNodeQueryService
    _SKIP_EDGE_TYPES: frozenset[EdgeType] = frozenset({EdgeType.DEFINES_MODULE})

    def execute(self, query: TraceSymbolDependenciesQuery) -> GraphViewDTO:
        detail = self.query_service.find_by_fqn(query.target_fqn)
        if detail is None:
            raise ValueError(f"Node with fqn '{query.target_fqn}' not found")
        root = self._build_tree(
            detail,
            query.direction,
            visited=set(),
            edge_type_filter=query.edge_type,
            depth=query.depth,
        )
        return GraphViewDTO(root=root)

    def _build_tree(
        self,
        detail: CodeNodeDetailDto,
        direction: EdgeDirection,
        visited: set[str],
        edge_type_filter: EdgeType | None = None,
        depth: int = 1,
    ) -> GraphViewNode:
        """递归构建以 detail 为根的依赖子树。depth 控制最大递归层数。"""
        visited.add(detail.fqn)
        children: list[GraphViewNode] = []
        if depth > 0:
            edges = (
                detail.outbound_edges
                if direction == EdgeDirection.OUT
                else detail.inbound_edges
            )
            for edge in edges:
                if edge.kind in self._SKIP_EDGE_TYPES:
                    continue
                if edge_type_filter is not None and edge.kind != edge_type_filter:
                    continue
                next_fqn = edge.fqn
                if next_fqn in visited:
                    continue
                child_detail = self.query_service.find_by_fqn(next_fqn)
                if child_detail is None:
                    continue
                child_node = self._build_tree(
                    child_detail, direction, visited, edge_type_filter, depth=depth - 1
                )
                child_node.edge_type = edge.kind
                children.append(child_node)
        return GraphViewNode(node=_detail_to_node(detail), children=children)

    @staticmethod
    def group_children_by_edge_type(
        children: list[GraphViewNode],
    ) -> list[GraphViewNode]:
        """将子节点按 edge_type 分组：CONTAINS 边直接展示，其余归入分组节点。"""
        grouped: dict[EdgeType | None, list[GraphViewNode]] = defaultdict(list)
        for child in children:
            grouped[child.edge_type].append(child)
        result: list[GraphViewNode] = []
        result.extend(grouped.pop(None, []))
        result.extend(grouped.pop(EdgeType.DEFINES, []))
        for edge_type in sorted(grouped, key=lambda e: str(e)):
            section = GraphViewNode(
                node=None, edge_type=edge_type, children=grouped[edge_type]
            )
            result.append(section)
        return result


def _detail_to_node(detail: CodeNodeDetailDto) -> CodeNode:
    """将 CodeNodeDetailDto 降级为 CodeNode（用于树节点存储）。"""
    outbound_edges = detail.outbound_edges
    match detail.kind:
        case CodeNodeKind.DIRECTORY:
            return DirectoryNode(
                id=detail.fqn, name=detail.name, outbound_edges=outbound_edges
            )
        case CodeNodeKind.FILE:
            return FileNode(
                id=detail.fqn, name=detail.name, outbound_edges=outbound_edges
            )
        case CodeNodeKind.MODULE:
            return ModuleNode(
                id=detail.fqn,
                name=detail.name,
                is_package=bool(detail.properties.get("is_package", False)),
                outbound_edges=outbound_edges,
            )
        case CodeNodeKind.CLASS:
            return ClassNode(
                id=detail.fqn, name=detail.name, outbound_edges=outbound_edges
            )
        case CodeNodeKind.FUNCTION:
            return FunctionNode(
                id=detail.fqn, name=detail.name, outbound_edges=outbound_edges
            )
        case CodeNodeKind.METHOD:
            return MethodNode(
                id=detail.fqn, name=detail.name, outbound_edges=outbound_edges
            )
        case CodeNodeKind.VARIABLE:
            return VariableNode(
                id=detail.fqn, name=detail.name, outbound_edges=outbound_edges
            )
        case CodeNodeKind.EXTERNAL:
            return ExternalNode(
                id=detail.fqn, name=detail.name, outbound_edges=outbound_edges
            )
