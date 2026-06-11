"""ClassNode 的三向转换（ORM ↔ Domain ↔ DTO）。"""

from __future__ import annotations
from typing import Any
from codegen.code_metadata.domain.aggregates.code_node import ClassNode
from codegen.code_metadata.domain.value_objects.ast_expr import ast_expr_adapter
from codegen.code_metadata.domain.value_objects.ast_type_param import type_param_adapter
from codegen.code_metadata.infrastructure.mappers.code_edge_mapper.dispatcher import (
    to_outbound_edges,
)
from codegen.code_metadata.infrastructure.orm_models.code_node_model import (
    ClassNodeModel,
)


class ClassNodeMapper:
    """ClassNode 专属的三向 Mapper。"""

    @classmethod
    def to_dto(cls, orm_model: ClassNodeModel) -> ClassNode:
        decorator_list = [
            ast_expr_adapter.validate_python(decorator)
            for decorator in orm_model.decorator_list
        ]
        bases = [ast_expr_adapter.validate_python(base) for base in orm_model.bases]
        type_params = [
            type_param_adapter.validate_python(tp) for tp in orm_model.type_params
        ]
        return ClassNode(
            id=orm_model.fqn,
            name=orm_model.name,
            description=orm_model.description,
            outbound_edges=to_outbound_edges(orm_model.outbound_edges),
            decorator_list=decorator_list,
            bases=bases,
            type_params=type_params,
        )

    @classmethod
    def to_properties(cls, dto: ClassNode) -> dict[str, Any]:
        decorator_list = [
            ast_expr_adapter.dump_python(decorator, mode="json")
            for decorator in dto.decorator_list
        ]
        bases = [ast_expr_adapter.dump_python(base, mode="json") for base in dto.bases]
        type_params = [
            type_param_adapter.dump_python(tp, mode="json") for tp in dto.type_params
        ]
        return {
            "decorator_list": decorator_list,
            "bases": bases,
            "type_params": type_params,
        }
