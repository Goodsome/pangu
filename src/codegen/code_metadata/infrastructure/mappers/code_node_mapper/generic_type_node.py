"""GenericTypeNode 的三向转换（ORM ↔ Domain ↔ DTO）。"""

from __future__ import annotations
from typing import Any
from codegen.code_metadata.domain.aggregates.code_node import GenericTypeNode
from codegen.code_metadata.infrastructure.mappers.code_edge_mapper.dispatcher import (
    to_outbound_edges,
)
from codegen.code_metadata.infrastructure.orm_models.code_node_model import (
    GenericTypeNodeModel,
)


class GenericTypeNodeMapper:
    """GenericTypeNode 专属的三向 Mapper。"""

    @classmethod
    def to_dto(cls, orm_model: GenericTypeNodeModel) -> GenericTypeNode:
        return GenericTypeNode(
            id=orm_model.fqn,
            name=orm_model.name,
            description=orm_model.description,
            outbound_edges=to_outbound_edges(orm_model.outbound_edges),
        )

    @classmethod
    def to_properties(cls, dto: GenericTypeNode) -> dict[str, Any]:
        return {}
