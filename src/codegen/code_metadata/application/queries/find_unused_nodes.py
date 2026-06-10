from dataclasses import dataclass
from codegen.code_metadata.domain.aggregates.code_node import CodeNode
from codegen.code_metadata.application.ports.code_node_query_service import (
    CodeNodeQueryService,
)
from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind


@dataclass
class FindUnusedNodes:
    """查询指定类型下未被使用的节点。"""

    query_service: CodeNodeQueryService

    def execute(self, kind: CodeNodeKind) -> list[CodeNode]:
        return self.query_service.find_unused_nodes(kind)
