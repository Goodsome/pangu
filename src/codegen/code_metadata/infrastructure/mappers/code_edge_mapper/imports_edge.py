"""ImportsEdge Mapper — 含 is_type_checking 属性。"""

from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Any
from codegen.code_metadata.domain.enums.edge_direction import EdgeDirection
from codegen.code_metadata.domain.value_objects.code_edge import ImportsEdge
from codegen.code_metadata.infrastructure.mappers.code_edge_mapper.base_mapper import (
    BaseEdgeMapper,
)

if TYPE_CHECKING:
    from codegen.code_metadata.infrastructure.orm_models.code_edge_model import (
        CodeEdgeModel,
    )


class ImportsEdgeMapper(BaseEdgeMapper):

    @staticmethod
    def to_dto(edge_model: CodeEdgeModel, direction: EdgeDirection) -> ImportsEdge:
        return ImportsEdge(
            fqn=BaseEdgeMapper._get_target_fqn(edge_model, direction),
            direction=direction,
            asname=edge_model.properties.get("asname"),
            is_type_checking=edge_model.properties.get("is_type_checking", False),
        )

    @staticmethod
    def to_properties(dto: ImportsEdge) -> dict[str, Any]:
        return {"asname": dto.asname, "is_type_checking": dto.is_type_checking}
