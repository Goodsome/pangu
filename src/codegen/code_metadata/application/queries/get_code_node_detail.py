from dataclasses import dataclass
from codegen.code_metadata.application.dtos.code_node_detail_dto import (
    CodeNodeDetailDto,
)
from codegen.code_metadata.application.dtos.get_code_node_query import GetCodeNodeQuery
from codegen.code_metadata.application.ports.code_node_query_service import (
    CodeNodeQueryService,
)


@dataclass
class GetCodeNodeDetail:
    """查询单个 CodeNode 的详情（含入边和出边），支持 ID 或 FQN。"""

    query_service: CodeNodeQueryService

    def execute(self, query: GetCodeNodeQuery) -> CodeNodeDetailDto:
        if query.node_id is not None:
            dto = self.query_service.find_by_id(query.node_id)
            if dto is None:
                raise ValueError(f"CodeNode with id '{query.node_id}' not found")
            return dto
        if query.fqn is not None:
            dto = self.query_service.find_by_fqn(query.fqn)
            if dto is None:
                raise ValueError(f"CodeNode with fqn '{query.fqn}' not found")
            return dto
        raise ValueError("Either 'node_id' or 'fqn' must be provided")
