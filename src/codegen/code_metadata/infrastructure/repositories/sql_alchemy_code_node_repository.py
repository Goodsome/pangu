"""CodeNodeRepository 的 SQLAlchemy 实现。传入的 ID (Fqn) 对应数据库中的 fqn 字段。"""

from collections.abc import Collection
from dataclasses import dataclass
from typing import override
from sqlalchemy import ColumnElement
from sqlalchemy import any_
from sqlalchemy import func
from sqlalchemy import or_
from sqlalchemy import update
from sqlalchemy import exists
from sqlalchemy import not_
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm import aliased
from sqlalchemy.orm import selectinload
from codegen.code_metadata.domain.aggregates.code_edge import CodeEdgeAggregate
from codegen.code_metadata.domain.aggregates.code_node import CodeNode
from codegen.code_metadata.domain.core.fqn import Fqn
from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind
from codegen.code_metadata.domain.enums.edge_type import EdgeType
from codegen.code_metadata.domain.ports.code_node_repository import CodeNodeRepository
from codegen.code_metadata.infrastructure.mappers.code_node_mapper.dispatcher import (
    dto_to_upsert_dict,
)
from codegen.code_metadata.infrastructure.mappers.code_node_mapper.dispatcher import (
    orm_to_dto,
)
from codegen.code_metadata.infrastructure.orm_models.code_edge_model import (
    CodeEdgeModel,
)
from codegen.code_metadata.infrastructure.orm_models.code_node_model import (
    ClassNodeModel,
)
from codegen.code_metadata.infrastructure.orm_models.code_node_model import (
    CodeNodeModel,
)
from codegen.code_metadata.infrastructure.orm_models.code_node_model import (
    DirectoryNodeModel,
)
from codegen.code_metadata.infrastructure.orm_models.code_node_model import (
    ExternalNodeModel,
)
from codegen.code_metadata.infrastructure.orm_models.code_node_model import (
    FileNodeModel,
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
    CodeNodeKind.PARAMETER: ParameterNodeModel,
    CodeNodeKind.EXTERNAL: ExternalNodeModel,
}


def _create_orm_model(dto: CodeNode, sync_id: str | None = None) -> CodeNodeModel:
    """从领域聚合根创建一个新的 ORM 模型实例。"""
    upsert_dict = dto_to_upsert_dict(dto, sync_id or "")
    model_cls = _KIND_TO_MODEL[dto.kind]
    return model_cls(**upsert_dict)


@dataclass
class SqlAlchemyCodeNodeRepository(CodeNodeRepository):
    """CodeNode 仓储的 SQLAlchemy 实现。 所有通过 Fqn 的查询均对应数据库的 fqn 字段（非主键 id）。"""

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
    def find_empty_modules(self, fqns: Collection[Fqn] | None = None) -> list[CodeNode]:
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
    def find_edges(
        self,
        edge_types: Collection[EdgeType] | None = None,
        source_fqns: Collection[Fqn] | None = None,
        target_fqns: Collection[Fqn] | None = None,
        source_fqn_prefixes: Collection[Fqn] | None = None,
        target_fqn_prefixes: Collection[Fqn] | None = None,
    ) -> list[CodeEdgeAggregate]:
        source_node = aliased(CodeNodeModel)
        target_node = aliased(CodeNodeModel)
        stmt = (
            select(
                source_node.fqn.label("source_fqn"),
                target_node.fqn.label("target_fqn"),
                CodeEdgeModel.type.label("edge_type"),
            )
            .join(source_node, CodeEdgeModel.source_id == source_node.id)
            .join(target_node, CodeEdgeModel.target_id == target_node.id)
        )
        conditions: list[ColumnElement[bool]] = []
        if edge_types is not None:
            conditions.append(CodeEdgeModel.type.in_(edge_types))
        if source_fqns is not None:
            conditions.append(source_node.fqn.in_(source_fqns))
        if target_fqns is not None:
            conditions.append(target_node.fqn.in_(target_fqns))
        if source_fqn_prefixes is not None:
            patterns = [f"{p}%" for p in source_fqn_prefixes]
            conditions.append(source_node.fqn.like(any_(patterns)))
        if target_fqn_prefixes is not None:
            patterns = [f"{p}%" for p in target_fqn_prefixes]
            conditions.append(target_node.fqn.like(any_(patterns)))
        if conditions:
            stmt = stmt.where(*conditions)
        rows = self.session.execute(stmt).all()
        return [
            CodeEdgeAggregate(
                source_id=Fqn(r.source_fqn),
                target_id=Fqn(r.target_fqn),
                edge_type=EdgeType(r.edge_type),
            )
            for r in rows
        ]

    def _get_orm(self, id: Fqn) -> CodeNodeModel:
        stmt = select(CodeNodeModel).where(CodeNodeModel.fqn == id)
        orm_model = self.session.execute(stmt).scalar_one_or_none()
        if orm_model is None:
            raise ValueError(f"CodeNode with fqn '{id}' not found")
        return orm_model

    @override
    def move_node(self, node_fqn: Fqn, target_fqn: Fqn) -> Fqn:
        node = self._get_orm(node_fqn)
        target = self._get_orm(target_fqn)
        match (node, target):
            case [ModuleNodeModel(), ModuleNodeModel()]:
                return self._move_module_node(node, target)
            case _:
                raise NotImplementedError(f"node.kind={node.kind!r}, {target.kind}=")

    def _move_module_node(self, node: ModuleNodeModel, target: ModuleNodeModel) -> Fqn:
        old_fqn = node.fqn
        new_fqn = f"{target.fqn}.{node.name}"
        if old_fqn == new_fqn:
            return Fqn(new_fqn)
        conflict_exists = self.session.scalar(
            select(CodeNodeModel.id).where(CodeNodeModel.fqn == new_fqn)
        )
        if conflict_exists:
            raise ValueError(f"目标路径已存在相同的 FQN: {new_fqn}")
        separator = "." if node.is_package else "::"
        like_pattern = f"{old_fqn}{separator}%"
        old_fqn_len = len(old_fqn)
        node_update_stmt = (
            update(CodeNodeModel)
            .where(
                or_(CodeNodeModel.id == node.id, CodeNodeModel.fqn.like(like_pattern))
            )
            .values(fqn=new_fqn + func.substr(CodeNodeModel.fqn, old_fqn_len + 1))
        )
        edge_update_stmt = (
            update(CodeEdgeModel)
            .where(
                CodeEdgeModel.target_id == node.id,
                CodeEdgeModel.type == EdgeType.CONTAINS,
            )
            .values(source_id=target.id)
        )
        self.session.execute(node_update_stmt)
        self.session.execute(edge_update_stmt)
        self.session.flush()
        return Fqn(new_fqn)
