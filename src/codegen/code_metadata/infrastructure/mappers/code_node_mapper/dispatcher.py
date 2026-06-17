from __future__ import annotations
from typing import Any
from typing import assert_never
from typing import cast
from codegen.code_metadata.application.dtos.code_node_detail_dto import (
    CodeNodeDetailDto,
)
from codegen.code_metadata.domain.aggregates.code_node import ClassNode
from codegen.code_metadata.domain.aggregates.code_node import CodeNode
from codegen.code_metadata.domain.aggregates.code_node import ExternalNode
from codegen.code_metadata.domain.aggregates.code_node import FunctionNode
from codegen.code_metadata.domain.aggregates.code_node import MethodNode
from codegen.code_metadata.domain.aggregates.code_node import ModuleNode
from codegen.code_metadata.domain.aggregates.code_node import ParameterNode
from codegen.code_metadata.domain.aggregates.code_node import TypeClassNode
from codegen.code_metadata.domain.aggregates.code_node import VariableNode
from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind
from codegen.code_metadata.infrastructure.mappers.code_edge_mapper.dispatcher import (
    to_inbound_edges,
)
from codegen.code_metadata.infrastructure.mappers.code_edge_mapper.dispatcher import (
    to_outbound_edges,
)
from codegen.code_metadata.infrastructure.orm_models.code_node_model import (
    ClassNodeModel,
)
from codegen.code_metadata.infrastructure.orm_models.code_node_model import (
    CodeNodeModel,
)
from codegen.code_metadata.infrastructure.orm_models.code_node_model import (
    ExternalNodeModel,
)
from codegen.code_metadata.infrastructure.orm_models.code_node_model import (
    FunctionNodeModel,
)
from codegen.code_metadata.infrastructure.orm_models.code_node_model import (
    MethodNodeModel,
)
from codegen.code_metadata.infrastructure.orm_models.code_node_model import (
    ModuleNodeModel,
)
from codegen.code_metadata.infrastructure.orm_models.code_node_model import (
    ParameterNodeModel,
)
from codegen.code_metadata.infrastructure.orm_models.code_node_model import (
    TypeClassNodeModel,
)
from codegen.code_metadata.infrastructure.orm_models.code_node_model import (
    VariableNodeModel,
)
from codegen.code_metadata.infrastructure.mappers.code_node_mapper.class_node import (
    ClassNodeMapper,
)
from codegen.code_metadata.infrastructure.mappers.code_node_mapper.external_node import (
    ExternalNodeMapper,
)
from codegen.code_metadata.infrastructure.mappers.code_node_mapper.function_node import (
    FunctionNodeMapper,
)
from codegen.code_metadata.infrastructure.mappers.code_node_mapper.method_node import (
    MethodNodeMapper,
)
from codegen.code_metadata.infrastructure.mappers.code_node_mapper.module_node import (
    ModuleNodeMapper,
)
from codegen.code_metadata.infrastructure.mappers.code_node_mapper.parameter_node import (
    ParameterNodeMapper,
)
from codegen.code_metadata.infrastructure.mappers.code_node_mapper.type_class_node import (
    TypeClassNodeMapper,
)
from codegen.code_metadata.infrastructure.mappers.code_node_mapper.variable_node import (
    VariableNodeMapper,
)


def orm_to_dto(orm_model: CodeNodeModel) -> CodeNode:
    """基于 kind 属性将 ORM 模型安全分发至 DTO 转换逻辑"""
    kind = CodeNodeKind(orm_model.kind)
    match kind:
        case CodeNodeKind.MODULE:
            return ModuleNodeMapper.to_dto(cast(ModuleNodeModel, orm_model))
        case CodeNodeKind.CLASS:
            return ClassNodeMapper.to_dto(cast(ClassNodeModel, orm_model))
        case CodeNodeKind.FUNCTION:
            return FunctionNodeMapper.to_dto(cast(FunctionNodeModel, orm_model))
        case CodeNodeKind.METHOD:
            return MethodNodeMapper.to_dto(cast(MethodNodeModel, orm_model))
        case CodeNodeKind.VARIABLE:
            return VariableNodeMapper.to_dto(cast(VariableNodeModel, orm_model))
        case CodeNodeKind.PARAMETER:
            return ParameterNodeMapper.to_dto(cast(ParameterNodeModel, orm_model))
        case CodeNodeKind.EXTERNAL:
            return ExternalNodeMapper.to_dto(cast(ExternalNodeModel, orm_model))
        case CodeNodeKind.TYPE_CLASS:
            return TypeClassNodeMapper.to_dto(cast(TypeClassNodeModel, orm_model))
        case _:
            assert_never(kind)


def orm_to_detail_dto(orm_model: CodeNodeModel) -> CodeNodeDetailDto:
    outbound_edges = to_outbound_edges(orm_model.outbound_edges)
    inbound_edges = to_inbound_edges(orm_model.inbound_edges)
    return CodeNodeDetailDto(
        id=orm_model.id,
        fqn=orm_model.fqn,
        name=orm_model.name,
        kind=CodeNodeKind(orm_model.kind),
        description=orm_model.description,
        properties=orm_model.properties,
        outbound_edges=outbound_edges,
        inbound_edges=inbound_edges,
    )


def dto_to_upsert_dict(dto: CodeNode, sync_id: str) -> dict[str, Any]:
    """高性能批量同步分发"""
    match dto:
        case ModuleNode():
            properties = ModuleNodeMapper.to_properties(dto)
        case ClassNode():
            properties = ClassNodeMapper.to_properties(dto)
        case FunctionNode():
            properties = FunctionNodeMapper.to_properties(dto)
        case MethodNode():
            properties = MethodNodeMapper.to_properties(dto)
        case VariableNode():
            properties = VariableNodeMapper.to_properties(dto)
        case ParameterNode():
            properties = ParameterNodeMapper.to_properties(dto)
        case ExternalNode():
            properties = ExternalNodeMapper.to_properties(dto)
        case TypeClassNode():
            properties = TypeClassNodeMapper.to_properties(dto)
        case _:
            assert_never(dto)
    return {
        "fqn": dto.id,
        "kind": dto.kind.value,
        "name": dto.name,
        "description": dto.description,
        "properties": properties,
        "last_sync_id": sync_id,
    }
