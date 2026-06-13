"""CodeNodeRepository 的 SQLAlchemy 实现。传入的 ID (Fqn) 对应数据库中的 fqn 字段。"""

from collections.abc import Collection
from dataclasses import dataclass
from typing import override

from sqlalchemy import ColumnElement, exists, not_, select
from sqlalchemy.orm import Session, selectinload

from codegen.code_metadata.domain.aggregates.code_node import CodeNode
from codegen.code_metadata.domain.core.fqn import Fqn
from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind
from codegen.code_metadata.domain.enums.edge_type import EdgeType
from codegen.code_metadata.domain.ports.code_node_repository import CodeNodeRepository
from codegen.code_metadata.infrastructure.mappers.code_node_mapper.dispatcher import (
    dto_to_upsert_dict,
    orm_to_dto,
)
from codegen.code_metadata.infrastructure.orm_models.code_edge_model import (
    CodeEdgeModel,
)
from codegen.code_metadata.infrastructure.orm_models.code_node_model import (
    ClassNodeModel,
    CodeNodeModel,
    DirectoryNodeModel,
    ExternalNodeModel,
    FileNodeModel,
    FunctionNodeModel,
    MethodNodeModel,
    ModuleNodeModel,
    VariableNodeModel,
)

_KIND_TO_MODEL: dict[CodeNodeKind, type[CodeNodeModel]] = {
    CodeNodeKind.DIRECTORY: DirectoryNodeModel,
    CodeNodeKind.FILE: FileNodeModel,
    CodeNodeKind.MODULE: ModuleNodeModel,
    CodeNodeKind.CLASS: ClassNodeModel,
    CodeNodeKind.FUNCTION: FunctionNodeModel,
    CodeNodeKind.METHOD: MethodNodeModel,
    CodeNodeKind.VARIABLE: VariableNodeModel,
    CodeNodeKind.EXTERNAL: ExternalNodeModel,
}


def _create_orm_model(dto: CodeNode, sync_id: str | None = None) -> CodeNodeModel:
    """从领域聚合根创建一个新的 ORM 模型实例。"""
    upsert_dict = dto_to_upsert_dict(dto, sync_id or "")
    model_cls = _KIND_TO_MODEL[dto.kind]
    return model_cls(**upsert_dict)


@dataclass
class SqlAlchemyCodeNodeRepository(CodeNodeRepository):
    """CodeNode 仓储的 SQLAlchemy 实现。

    所有通过 Fqn 的查询均对应数据库的 fqn 字段（非主键 id）。
    """

    session: Session

    @override
    def _add(self, aggregate: CodeNode) -> None:
        orm_model = _create_orm_model(aggregate)
        self.session.add(orm_model)

    @override
    def _add_all(self, aggregates: list[CodeNode]) -> None:
        orm_models = [_create_orm_model(a) for a in aggregates]
        self.session.add_all(orm_models)

    @override
    def _get(self, id: Fqn) -> CodeNode:
        stmt = select(CodeNodeModel).where(CodeNodeModel.fqn == id)
        orm_model = self.session.execute(stmt).scalar_one_or_none()
        if orm_model is None:
            raise ValueError(f"CodeNode with fqn '{id}' not found")
        return orm_to_dto(orm_model)

    @override
    def _save(self, aggregate: CodeNode) -> None:
        stmt = select(CodeNodeModel).where(CodeNodeModel.fqn == aggregate.id)
        orm_model = self.session.execute(stmt).scalar_one_or_none()
        if orm_model is None:
            raise ValueError(f"CodeNode with fqn '{aggregate.id}' not found")
        upsert_dict = dto_to_upsert_dict(aggregate, orm_model.last_sync_id or "")
        for key, value in upsert_dict.items():
            setattr(orm_model, key, value)

    @override
    def _save_all(self, aggregates: list[CodeNode]) -> None:
        if not aggregates:
            return
        fqns = [a.id for a in aggregates]
        stmt = select(CodeNodeModel).where(CodeNodeModel.fqn.in_(fqns))
        existing_models = {m.fqn: m for m in self.session.execute(stmt).scalars().all()}
        for aggregate in aggregates:
            orm_model = existing_models.get(aggregate.id)
            if orm_model is None:
                raise ValueError(f"CodeNode with fqn '{aggregate.id}' not found")
            upsert_dict = dto_to_upsert_dict(aggregate, orm_model.last_sync_id or "")
            for key, value in upsert_dict.items():
                setattr(orm_model, key, value)

    @override
    def _delete(self, aggregate: CodeNode) -> None:
        stmt = select(CodeNodeModel).where(CodeNodeModel.fqn == aggregate.id)
        orm_model = self.session.execute(stmt).scalar_one_or_none()
        if orm_model:
            self.session.delete(orm_model)

    @override
    def find_empty_modules(
        self,
        fqns: Collection[Fqn] | None = None,
    ) -> list[CodeNode]:
        self.session.flush()
        
        has_defines_outbound = exists().where(
            CodeEdgeModel.source_id == CodeNodeModel.id,
            CodeEdgeModel.type.in_((EdgeType.DEFINES, EdgeType.CONTAINS)),
        )
        conditions: list[ColumnElement[bool]] = [
            CodeNodeModel.kind == CodeNodeKind.MODULE,
            not_(has_defines_outbound),
        ]
        if fqns:
            conditions.append(CodeNodeModel.fqn.in_(fqns))

        stmt = (
            select(CodeNodeModel)
            .where(*conditions)
            .options(
                selectinload(CodeNodeModel.outbound_edges).joinedload(
                    CodeEdgeModel.target_entity
                )
            )
        )
        models = self.session.execute(stmt).scalars().unique().all()
        return [orm_to_dto(m) for m in models]


    @override
    def find_unused_nodes(
        self,
        kind: CodeNodeKind | None = None,
        fqns: Collection[str] | None = None,
    ) -> list[CodeNode]:
        _SUPPORTED = {
            CodeNodeKind.CLASS,
            CodeNodeKind.FUNCTION,
            CodeNodeKind.VARIABLE,
        }
        _USAGE_EDGE_TYPES = {
            EdgeType.IMPORTS,
            EdgeType.INHERITS,
            EdgeType.CALLS,
            EdgeType.RETURNS,
            EdgeType.ACCEPTS,
            EdgeType.TYPED_AS,
        }
        has_usage_inbound = exists().where(
            CodeEdgeModel.target_id == CodeNodeModel.id,
            CodeEdgeModel.type.in_(_USAGE_EDGE_TYPES),
        )
        conditions: list[ColumnElement[bool]] = [not_(has_usage_inbound)]
        if kind:
            conditions.append(CodeNodeModel.kind == kind)
        else:
            conditions.append(CodeNodeModel.kind.in_(_SUPPORTED))
        if fqns:
            conditions.append(CodeNodeModel.fqn.in_(fqns))

        stmt = (
            select(CodeNodeModel)
            .where(*conditions)
            .options(
                selectinload(CodeNodeModel.outbound_edges).joinedload(
                    CodeEdgeModel.target_entity
                )
            )
        )
        models = self.session.execute(stmt).scalars().unique().all()
        return [orm_to_dto(m) for m in models]