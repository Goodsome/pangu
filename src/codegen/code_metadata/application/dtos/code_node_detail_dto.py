from uuid import UUID
from pydantic import BaseModel
from pydantic import Field
from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind
from codegen.code_metadata.domain.value_objects.code_edge import CodeEdge


class CodeNodeDetailDto(BaseModel):
    """CodeNode 详情 DTO：包含 id、基本信息、出边和入边。"""

    id: UUID
    fqn: str
    name: str
    kind: CodeNodeKind
    description: str | None
    properties: dict[str, object]
    outbound_edges: list[CodeEdge] = Field(default_factory=list)
    inbound_edges: list[CodeEdge] = Field(default_factory=list)
