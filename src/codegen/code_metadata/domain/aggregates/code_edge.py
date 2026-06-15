from typing import override
from pydantic import BaseModel
from codegen.code_metadata.domain.core.fqn import Fqn
from codegen.code_metadata.domain.enums.edge_type import EdgeType


class CodeEdgeAggregate(BaseModel):
    source_id: Fqn
    target_id: Fqn
    edge_type: EdgeType

    @override
    def __hash__(self) -> int:
        return hash((self.source_id, self.target_id, self.edge_type))
