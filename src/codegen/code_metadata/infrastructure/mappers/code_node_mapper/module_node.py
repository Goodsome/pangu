"""ModuleNode 的三向转换（ORM ↔ Domain ↔ DTO）。"""

from __future__ import annotations
from typing import Any
from codegen.code_metadata.domain.aggregates.code_node import ModuleNode
from codegen.code_metadata.domain.value_objects.ast_expr import ast_expr_adapter
from codegen.code_metadata.infrastructure.mappers.code_edge_mapper.dispatcher import (
    to_outbound_edges,
)
from codegen.code_metadata.infrastructure.orm_models.code_node_model import (
    CodeNodeModel,
)
from codegen.code_metadata.infrastructure.orm_models.code_node_model import (
    ModuleNodeModel,
)


class ModuleNodeMapper:
    """ModuleNode 专属的三向 Mapper。"""

    @classmethod
    def to_dto(cls, orm_model: CodeNodeModel) -> ModuleNode:
        assert isinstance(orm_model, ModuleNodeModel)
        exprs = [ast_expr_adapter.validate_python(expr) for expr in orm_model.exprs]
        return ModuleNode(
            fqn=orm_model.fqn,
            name=orm_model.name,
            description=orm_model.description,
            is_package=orm_model.is_package,
            outbound_edges=to_outbound_edges(orm_model.outbound_edges),
            exprs=exprs,
        )

    @classmethod
    def to_properties(cls, dto: ModuleNode) -> dict[str, Any]:
        exprs = [ast_expr_adapter.dump_python(expr, mode="json") for expr in dto.exprs]
        return {"is_package": dto.is_package, "exprs": exprs}
