from pydantic import BaseModel
from codegen.code_metadata.domain.enums.edge_type import EdgeType
from codegen.code_metadata.domain.enums.edge_direction import EdgeDirection


class TraceSymbolDependenciesQuery(BaseModel):
    """CQRS 查询 DTO：追踪符号依赖关系。"""

    target_fqn: str
    direction: EdgeDirection
    edge_type: EdgeType | None = None
    depth: int = 1
