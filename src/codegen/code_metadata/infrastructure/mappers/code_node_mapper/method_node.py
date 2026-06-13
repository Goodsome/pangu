"""MethodNode 的三向转换（ORM ↔ Domain ↔ DTO）。"""

from __future__ import annotations
from typing import Any
from codegen.code_metadata.domain.aggregates.code_node import MethodNode
from codegen.code_metadata.domain.value_objects.ast_expr import ast_expr_adapter
from codegen.code_metadata.domain.value_objects.ast_stmt import ast_stmt_adapter
from codegen.code_metadata.infrastructure.mappers.code_edge_mapper.dispatcher import (
    to_outbound_edges,
)
from codegen.code_metadata.infrastructure.orm_models.code_node_model import (
    MethodNodeModel,
)


class MethodNodeMapper:
    """MethodNode 专属的三向 Mapper。"""

    @classmethod
    def to_dto(cls, orm_model: MethodNodeModel) -> MethodNode:
        decorator_list = [
            ast_expr_adapter.validate_python(decorator)
            for decorator in orm_model.decorator_list
        ]
        returns = (
            ast_expr_adapter.validate_python(orm_model.returns)
            if orm_model.returns
            else None
        )
        body = [ast_stmt_adapter.validate_python(stmt) for stmt in orm_model.body]
        return MethodNode(
            id=orm_model.fqn,
            name=orm_model.name,
            outbound_edges=to_outbound_edges(orm_model.outbound_edges),
            is_async=orm_model.is_async,
            decorator_list=decorator_list,
            returns=returns,
            body=body,
        )

    @classmethod
    def to_properties(cls, dto: MethodNode) -> dict[str, Any]:
        decorator_list = [
            ast_expr_adapter.dump_python(decorator, mode="json")
            for decorator in dto.decorator_list
        ]
        returns = (
            ast_expr_adapter.dump_python(dto.returns, mode="json")
            if dto.returns
            else None
        )
        body = [ast_stmt_adapter.dump_python(stmt, mode="json") for stmt in dto.body]
        return {
            "is_async": dto.is_async,
            "decorator_list": decorator_list,
            "returns": returns,
            "body": body,
        }
