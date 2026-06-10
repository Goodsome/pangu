"""Edge Mapper 基类：ORM → Domain 边的公共转换。"""

from __future__ import annotations
from typing import TYPE_CHECKING
from codegen.code_metadata.domain.enums.edge_direction import EdgeDirection

if TYPE_CHECKING:
    from codegen.code_metadata.infrastructure.orm_models.code_edge_model import (
        CodeEdgeModel,
    )


class BaseEdgeMapper:
    """所有边类型 Mapper 的公共基类。"""

    @staticmethod
    def _get_target_fqn(edge_model: CodeEdgeModel, direction: EdgeDirection) -> str:
        """根据方向取对端 FQN。"""
        if direction == EdgeDirection.OUT:
            return edge_model.target_entity.fqn
        return edge_model.source_entity.fqn
