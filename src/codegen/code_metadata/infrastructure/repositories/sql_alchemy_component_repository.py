from collections.abc import Collection
from dataclasses import dataclass
from typing import override
from sqlalchemy import ColumnElement
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import tuple_
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload
from codegen.code_metadata.application.dtos.component_filter import ComponentFilter
from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.ports.component_repository import ComponentRepository
from codegen.code_metadata.infrastructure.mappers.component_mapper import (
    ComponentMapper,
)
from codegen.code_metadata.infrastructure.orm_models.behavior_model import BehaviorModel
from codegen.code_metadata.infrastructure.orm_models.component_model import (
    ClassComponentModel,
)
from codegen.code_metadata.infrastructure.orm_models.component_model import (
    ComponentModel,
)
from codegen.shared.application.dtos.page import Page
from codegen.shared.application.dtos.page_query import PageQuery


@dataclass
class SqlAlchemyComponentRepository(ComponentRepository):
    """Component 仓储的 SQLAlchemy 实现。 负责管理 Component 聚合根的持久化生命周期，隔离基础设施层与领域层。"""

    session: Session

    @override
    def _add(self, aggregate: Component) -> None:
        """新增一个 Component 聚合根到数据库。"""
        orm_model = ComponentMapper.to_orm(aggregate)
        self.session.add(orm_model)

    @override
    def _add_all(self, aggregates: list[Component]) -> None:
        """批量新增 Component 聚合根到数据库。"""
        orm_models = [ComponentMapper.to_orm(aggregate) for aggregate in aggregates]
        self.session.add_all(orm_models)

    @override
    def _get(self, id: ComponentId) -> Component:
        """根据 ID 获取 Component 聚合根。如果找不到则抛出异常。"""
        orm_model = self.session.get(
            ComponentModel,
            id.value,
            options=[
                selectinload(ClassComponentModel.attributes),
                selectinload(ClassComponentModel.behaviors).selectinload(
                    BehaviorModel.inputs
                ),
            ],
        )
        if orm_model is None:
            raise ValueError(f"Component with id {id.value} not found")
        return ComponentMapper.to_domain(orm_model)

    @override
    def _save(self, aggregate: Component) -> None:
        """更新现有的 Component 聚合根。"""
        orm_model = ComponentMapper.to_orm(aggregate)
        self.session.merge(orm_model)

    @override
    def _save_all(self, aggregates: list[Component]) -> None:
        if not aggregates:
            return
        orm_models = [ComponentMapper.to_orm(aggregate) for aggregate in aggregates]
        for orm_model in orm_models:
            self.session.merge(orm_model)

    @override
    def _delete(self, aggregate: Component) -> None:
        """删除 Component 聚合根及其所有下属实体。"""
        model = self.session.get(ComponentModel, aggregate.id.value)
        if model:
            self.session.delete(model)

    @override
    def find_page(self, page_query: PageQuery[ComponentFilter]) -> Page[Component]:
        conditions: list[ColumnElement[bool]] = []
        if page_query.condition.type is not None:
            conditions.append(ComponentModel.type == page_query.condition.type)
        if page_query.condition.context is not None:
            conditions.append(ComponentModel.context == page_query.condition.context)
        if page_query.condition.name is not None:
            conditions.append(ComponentModel.name == page_query.condition.name)
        stmt = (
            select(ComponentModel)
            .where(*conditions)
            .options(
                selectinload(ClassComponentModel.attributes),
                selectinload(ClassComponentModel.behaviors).selectinload(
                    BehaviorModel.inputs
                ),
            )
        )
        total = (
            self.session.scalar(
                select(func.count()).select_from(ComponentModel).where(*conditions)
            )
            or 0
        )
        if page_query.current and page_query.size:
            offset = (page_query.current - 1) * page_query.size
            stmt = stmt.offset(offset).limit(page_query.size)
        models = self.session.execute(stmt).scalars().all()
        items = [ComponentMapper.to_domain(m) for m in models]
        return Page(
            items=items, total=total, current=page_query.current, size=page_query.size
        )

    @override
    def find_by_context_names(
        self, context_names: set[tuple[str, str]]
    ) -> dict[tuple[str, str], Component]:
        if not context_names:
            return {}
        stmt = (
            select(ComponentModel)
            .where(
                tuple_(ComponentModel.context, ComponentModel.name).in_(context_names)
            )
            .options(
                selectinload(ClassComponentModel.attributes),
                selectinload(ClassComponentModel.behaviors).selectinload(
                    BehaviorModel.inputs
                ),
            )
        )
        models = self.session.execute(stmt).scalars().all()
        return {(m.context, m.name): ComponentMapper.to_domain(m) for m in models}

    @override
    def find_by_contexts(self, contexts: set[str]) -> dict[tuple[str, str], Component]:
        if not contexts:
            return {}
        stmt = (
            select(ComponentModel)
            .where(ComponentModel.context.in_(contexts))
            .options(
                selectinload(ClassComponentModel.attributes),
                selectinload(ClassComponentModel.behaviors).selectinload(
                    BehaviorModel.inputs
                ),
            )
        )
        models = self.session.execute(stmt).scalars().all()
        return {(m.context, m.name): ComponentMapper.to_domain(m) for m in models}

    @override
    def find_by_ids(self, ids: Collection[ComponentId]) -> dict[ComponentId, Component]:
        if not ids:
            return {}
        unique_ids: set[str] = {str(i) for i in ids}
        stmt = (
            select(ComponentModel)
            .where(ComponentModel.id.in_(unique_ids))
            .options(
                selectinload(ClassComponentModel.attributes),
                selectinload(ClassComponentModel.behaviors).selectinload(
                    BehaviorModel.inputs
                ),
            )
        )
        models = self.session.execute(stmt).scalars().all()
        return {
            ComponentId.reconstitute(m.id): ComponentMapper.to_domain(m) for m in models
        }
