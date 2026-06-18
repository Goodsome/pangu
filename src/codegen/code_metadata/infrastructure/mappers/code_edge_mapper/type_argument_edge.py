"""TypeArgumentEdge Mapper。"""

from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Any
from codegen.code_metadata.domain.enums.edge_direction import EdgeDirection
from codegen.code_metadata.domain.value_objects.code_edge import TypeArgumentEdge
from codegen.code_metadata.infrastructure.mappers.code_edge_mapper.base_mapper import (
    BaseEdgeMapper,
)

if TYPE_CHECKING:
    from codegen.code_metadata.infrastructure.orm_models.code_edge_model import (
        CodeEdgeModel,
    )


class TypeArgumentEdgeMapper(BaseEdgeMapper):

    @staticmethod
    def to_dto(edge_model: CodeEdgeModel, direction: EdgeDirection) -> TypeArgumentEdge:
        return TypeArgumentEdge(
            fqn=BaseEdgeMapper._get_target_fqn(edge_model, direction),
            direction=direction,
        )

    @staticmethod
    def to_properties(dto: TypeArgumentEdge) -> dict[str, Any]:
        return {}
