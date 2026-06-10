"""基于 EdgeType 将 ORM 边分发至对应的 Edge Mapper。"""

from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Any
from typing import assert_never
from codegen.code_metadata.domain.enums.edge_direction import EdgeDirection
from codegen.code_metadata.domain.enums.edge_type import EdgeType
from codegen.code_metadata.domain.value_objects.code_edge import AcceptsEdge
from codegen.code_metadata.domain.value_objects.code_edge import CallsEdge
from codegen.code_metadata.domain.value_objects.code_edge import CodeEdge
from codegen.code_metadata.domain.value_objects.code_edge import ContainsEdge
from codegen.code_metadata.domain.value_objects.code_edge import DefinesEdge
from codegen.code_metadata.domain.value_objects.code_edge import DefinesModuleEdge
from codegen.code_metadata.domain.value_objects.code_edge import ExportsEdge
from codegen.code_metadata.domain.value_objects.code_edge import ImportsEdge
from codegen.code_metadata.domain.value_objects.code_edge import ImplementsEdge
from codegen.code_metadata.domain.value_objects.code_edge import InheritsEdge
from codegen.code_metadata.domain.value_objects.code_edge import ReadsEdge
from codegen.code_metadata.domain.value_objects.code_edge import ReturnsEdge
from codegen.code_metadata.domain.value_objects.code_edge import TypedAsEdge
from codegen.code_metadata.domain.value_objects.code_edge import WritesEdge
from codegen.code_metadata.infrastructure.mappers.code_edge_mapper.accepts_edge import (
    AcceptsEdgeMapper,
)
from codegen.code_metadata.infrastructure.mappers.code_edge_mapper.calls_edge import (
    CallsEdgeMapper,
)
from codegen.code_metadata.infrastructure.mappers.code_edge_mapper.contains_edge import (
    ContainsEdgeMapper,
)
from codegen.code_metadata.infrastructure.mappers.code_edge_mapper.defines_edge import (
    DefinesEdgeMapper,
)
from codegen.code_metadata.infrastructure.mappers.code_edge_mapper.defines_module_edge import (
    DefinesModuleEdgeMapper,
)
from codegen.code_metadata.infrastructure.mappers.code_edge_mapper.exports_edge import (
    ExportsEdgeMapper,
)
from codegen.code_metadata.infrastructure.mappers.code_edge_mapper.imports_edge import (
    ImportsEdgeMapper,
)
from codegen.code_metadata.infrastructure.mappers.code_edge_mapper.implements_edge import (
    ImplementsEdgeMapper,
)
from codegen.code_metadata.infrastructure.mappers.code_edge_mapper.inherits_edge import (
    InheritsEdgeMapper,
)
from codegen.code_metadata.infrastructure.mappers.code_edge_mapper.reads_edge import (
    ReadsEdgeMapper,
)
from codegen.code_metadata.infrastructure.mappers.code_edge_mapper.returns_edge import (
    ReturnsEdgeMapper,
)
from codegen.code_metadata.infrastructure.mappers.code_edge_mapper.typed_as_edge import (
    TypedAsEdgeMapper,
)
from codegen.code_metadata.infrastructure.mappers.code_edge_mapper.writes_edge import (
    WritesEdgeMapper,
)

if TYPE_CHECKING:
    from codegen.code_metadata.infrastructure.orm_models.code_edge_model import (
        CodeEdgeModel,
    )


def to_dto(edge_model: CodeEdgeModel, direction: EdgeDirection) -> CodeEdge:
    """将单个 ORM 边模型转换为对应类型的 Domain 边值对象。"""
    edge_type = EdgeType(edge_model.type)
    match edge_type:
        case EdgeType.CONTAINS:
            return ContainsEdgeMapper.to_dto(edge_model, direction)
        case EdgeType.DEFINES:
            return DefinesEdgeMapper.to_dto(edge_model, direction)
        case EdgeType.DEFINES_MODULE:
            return DefinesModuleEdgeMapper.to_dto(edge_model, direction)
        case EdgeType.IMPORTS:
            return ImportsEdgeMapper.to_dto(edge_model, direction)
        case EdgeType.EXPORTS:
            return ExportsEdgeMapper.to_dto(edge_model, direction)
        case EdgeType.INHERITS:
            return InheritsEdgeMapper.to_dto(edge_model, direction)
        case EdgeType.IMPLEMENTS:
            return ImplementsEdgeMapper.to_dto(edge_model, direction)
        case EdgeType.CALLS:
            return CallsEdgeMapper.to_dto(edge_model, direction)
        case EdgeType.READS:
            return ReadsEdgeMapper.to_dto(edge_model, direction)
        case EdgeType.WRITES:
            return WritesEdgeMapper.to_dto(edge_model, direction)
        case EdgeType.TYPED_AS:
            return TypedAsEdgeMapper.to_dto(edge_model, direction)
        case EdgeType.RETURNS:
            return ReturnsEdgeMapper.to_dto(edge_model, direction)
        case EdgeType.ACCEPTS:
            return AcceptsEdgeMapper.to_dto(edge_model, direction)
        case _:
            assert_never(edge_type)


def to_outbound_edges(edge_models: list[CodeEdgeModel]) -> list[CodeEdge]:
    """批量转换出边。"""
    return [to_dto(e, EdgeDirection.OUT) for e in edge_models]


def to_inbound_edges(edge_models: list[CodeEdgeModel]) -> list[CodeEdge]:
    """批量转换入边。"""
    return [to_dto(e, EdgeDirection.IN) for e in edge_models]


def code_edge_to_upsert_dict(edge: CodeEdge) -> dict[str, Any]:
    """将 Domain 边值对象转换为可直接用于 INSERT 的 dict（不含 source_id / target_id）。"""
    match edge:
        case ContainsEdge():
            properties = ContainsEdgeMapper.to_properties(edge)
        case DefinesEdge():
            properties = DefinesEdgeMapper.to_properties(edge)
        case DefinesModuleEdge():
            properties = DefinesModuleEdgeMapper.to_properties(edge)
        case ImportsEdge():
            properties = ImportsEdgeMapper.to_properties(edge)
        case ExportsEdge():
            properties = ExportsEdgeMapper.to_properties(edge)
        case InheritsEdge():
            properties = InheritsEdgeMapper.to_properties(edge)
        case ImplementsEdge():
            properties = ImplementsEdgeMapper.to_properties(edge)
        case CallsEdge():
            properties = CallsEdgeMapper.to_properties(edge)
        case ReadsEdge():
            properties = ReadsEdgeMapper.to_properties(edge)
        case WritesEdge():
            properties = WritesEdgeMapper.to_properties(edge)
        case TypedAsEdge():
            properties = TypedAsEdgeMapper.to_properties(edge)
        case ReturnsEdge():
            properties = ReturnsEdgeMapper.to_properties(edge)
        case AcceptsEdge():
            properties = AcceptsEdgeMapper.to_properties(edge)
        case _:
            assert_never(edge)
    return {"type": edge.kind.value, "properties": properties}
