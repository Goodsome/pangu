from uuid import UUID
from pydantic import BaseModel


class GetCodeNodeQuery(BaseModel):
    """CQRS 查询 DTO：按 ID 或 FQN 查询 CodeNode 详情。"""

    node_id: UUID | None = None
    fqn: str | None = None
