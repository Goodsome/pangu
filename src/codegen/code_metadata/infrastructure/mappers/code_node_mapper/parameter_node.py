"""ParameterNode 的三向转换（ORM ↔ Domain ↔ DTO）。"""

from __future__ import annotations
from typing import Any
from codegen.code_metadata.domain.aggregates.code_node import ParameterNode
from codegen.code_metadata.domain.value_objects.ast_expr import ast_expr_adapter
from codegen.code_metadata.infrastructure.mappers.code_edge_mapper.dispatcher import (
    to_outbound_edges,
)
from codegen.code_metadata.infrastructure.orm_models.code_node_model import (
    ParameterNodeModel,
)


class ParameterNodeMapper:
    """ParameterNode 专属的三向 Mapper。"""

    @classmethod
    def to_dto(cls, orm_model: ParameterNodeModel) -> ParameterNode:
        annotation = (
            ast_expr_adapter.validate_python(orm_model.annotation)
            if orm_model.annotation
            else None
        )
        value = (
            ast_expr_adapter.validate_python(orm_model.value)
            if orm_model.value
            else None
        )
        return ParameterNode(
            id=orm_model.fqn,
            name=orm_model.name,
            annotation=annotation,
            value=value,
            outbound_edges=to_outbound_edges(orm_model.outbound_edges),
        )

    @classmethod
    def to_properties(cls, dto: ParameterNode) -> dict[str, Any]:
        annotation = (
            ast_expr_adapter.dump_python(dto.annotation, mode="json")
            if dto.annotation
            else None
        )
        value = (
            ast_expr_adapter.dump_python(dto.value, mode="json") if dto.value else None
        )
        return {"annotation": annotation, "value": value}
