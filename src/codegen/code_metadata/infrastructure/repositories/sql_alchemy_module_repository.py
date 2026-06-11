from dataclasses import dataclass
from typing import override
from sqlalchemy import ColumnElement
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.orm import Session
from codegen.code_metadata.application.dtos.module_filter import ModuleFilter
from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.aggregates.module import Module
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.identifiers.module_id import ModuleId
from codegen.code_metadata.domain.ports.module_repository import ModuleRepository
from codegen.code_metadata.infrastructure.mappers.component_v2_mapper import (
    ComponentV2Mapper,
)
from codegen.code_metadata.infrastructure.mappers.module_mapper import ModuleMapper
from codegen.code_metadata.infrastructure.orm_models.component_v2_model import (
    ComponentV2Model,
)
from codegen.code_metadata.infrastructure.orm_models.module_model import ModuleModel
from codegen.shared.application.dtos.page import Page
from codegen.shared.application.dtos.page_query import PageQuery


@dataclass
class SqlAlchemyModuleRepository(ModuleRepository):
    """Module 仓储的 SQLAlchemy 实现。 负责管理 Module 聚合根的持久化生命周期，隔离基础设施层与领域层。"""

    session: Session

    @override
    def _add(self, aggregate: Module) -> None:
        orm_model = ModuleMapper.to_orm(aggregate)
        self.session.add(orm_model)

    @override
    def _add_all(self, aggregates: list[Module]) -> None:
        orm_models = [ModuleMapper.to_orm(a) for a in aggregates]
        self.session.add_all(orm_models)

    @override
    def _get(self, id: ModuleId) -> Module:
        orm_model = self.session.get(ModuleModel, id.value)
        if orm_model is None:
            raise ValueError(f"Module with id {id.value} not found")
        return ModuleMapper.to_domain(orm_model)

    @override
    def _save(self, aggregate: Module) -> None:
        orm_model = ModuleMapper.to_orm(aggregate)
        self.session.merge(orm_model)

    @override
    def _save_all(self, aggregates: list[Module]) -> None:
        if not aggregates:
            return
        orm_models = [ModuleMapper.to_orm(a) for a in aggregates]
        for orm_model in orm_models:
            self.session.merge(orm_model)

    @override
    def _delete(self, aggregate: Module) -> None:
        model = self.session.get(ModuleModel, aggregate.id.value)
        if model:
            self.session.delete(model)

    @override
    def find_by_ids(self, ids: list[ModuleId]) -> dict[ModuleId, Module]:
        if not ids:
            return {}
        unique_ids = {id.value for id in ids}
        stmt = select(ModuleModel).where(ModuleModel.id.in_(unique_ids))
        models = self.session.execute(stmt).scalars().all()
        return {ModuleId.reconstitute(m.id): ModuleMapper.to_domain(m) for m in models}

    @override
    def find_by_paths(self, paths: set[str]) -> dict[str, Module]:
        if not paths:
            return {}
        stmt = select(ModuleModel).where(ModuleModel.path.in_(paths))
        models = self.session.execute(stmt).scalars().all()
        return {m.path: ModuleMapper.to_domain(m) for m in models}

    @override
    def find_components_by_ids(
        self, component_ids: list[ComponentId]
    ) -> dict[ComponentId, Component]:
        if not component_ids:
            return {}
        unique_ids = {cid.value for cid in component_ids}
        stmt = select(ComponentV2Model).where(ComponentV2Model.id.in_(unique_ids))
        models = self.session.execute(stmt).scalars().all()
        return {
            ComponentId.reconstitute(m.id): ComponentV2Mapper.to_domain(m)
            for m in models
        }

    @staticmethod
    def _build_conditions(filter: ModuleFilter) -> list[ColumnElement[bool]]:
        conditions: list[ColumnElement[bool]] = []
        if filter.kind is not None:
            conditions.append(ModuleModel.kind == filter.kind)
        if filter.name is not None:
            conditions.append(ModuleModel.name == filter.name)
        if filter.path is not None:
            conditions.append(ModuleModel.path == filter.path)
        return conditions

    @override
    def find_by_filter(self, filter: ModuleFilter) -> list[Module]:
        conditions = self._build_conditions(filter)
        stmt = select(ModuleModel).where(*conditions)
        models = self.session.execute(stmt).scalars().all()
        return [ModuleMapper.to_domain(m) for m in models]

    @override
    def find_page(self, page_query: PageQuery[ModuleFilter]) -> Page[Module]:
        conditions = self._build_conditions(page_query.condition)
        stmt = select(ModuleModel).where(*conditions)
        total = (
            self.session.scalar(
                select(func.count()).select_from(ModuleModel).where(*conditions)
            )
            or 0
        )
        if page_query.current and page_query.size:
            offset = (page_query.current - 1) * page_query.size
            stmt = stmt.offset(offset).limit(page_query.size)
        models = self.session.execute(stmt).scalars().all()
        items = [ModuleMapper.to_domain(m) for m in models]
        return Page(
            items=items, total=total, current=page_query.current, size=page_query.size
        )
