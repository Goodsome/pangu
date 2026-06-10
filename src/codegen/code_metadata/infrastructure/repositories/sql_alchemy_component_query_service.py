from collections.abc import Collection
from dataclasses import dataclass
from typing import override
from sqlalchemy import ColumnElement
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import tuple_
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from codegen.code_metadata.application.dtos.component_dto import ComponentDto
from codegen.code_metadata.application.dtos.component_filter import ComponentFilter
from codegen.code_metadata.application.ports.component_query_service import (
    ComponentQueryService,
)
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.infrastructure.mappers.component_mapper import (
    ComponentMapper,
)
from codegen.code_metadata.infrastructure.orm_models.component_model import (
    ComponentModel,
)
from codegen.shared.application.dtos.page import Page
from codegen.shared.application.dtos.page_query import PageQuery


@dataclass
class SqlAlchemyComponentQueryService(ComponentQueryService):
    session_factory: sessionmaker[Session]

    @override
    def find_by_name(self, name: str, context: str) -> ComponentDto | None:
        stmt = select(ComponentModel).where(
            ComponentModel.name == name, ComponentModel.context == context
        )
        with self.session_factory() as session:
            model = session.execute(stmt).scalar_one_or_none()
        if model is None:
            return None
        dto = ComponentMapper.to_dto(model)
        return dto

    @override
    def find_page(self, query: PageQuery[ComponentFilter]) -> Page[ComponentDto]:
        conditions: list[ColumnElement[bool]] = []
        if query.condition.type is not None:
            conditions.append(ComponentModel.type == query.condition.type)
        if query.condition.context is not None:
            conditions.append(ComponentModel.context == query.condition.context)
        if query.condition.name is not None:
            conditions.append(ComponentModel.name == query.condition.name)
        stmt = select(ComponentModel).where(*conditions)
        with self.session_factory() as session:
            total = (
                session.scalar(
                    select(func.count()).select_from(ComponentModel).where(*conditions)
                )
                or 0
            )
            if query.current and query.size:
                offset = (query.current - 1) * query.size
                stmt = stmt.offset(offset=offset).limit(query.size)
            models = session.execute(stmt).scalars().all()
        items = [ComponentMapper.to_dto(m) for m in models]
        return Page(items=items, total=total, current=query.current, size=query.size)

    @override
    def find_by_context_names(
        self, context_names: set[tuple[str, str]]
    ) -> list[ComponentDto]:
        if not context_names:
            return []
        stmt = select(ComponentModel).where(
            tuple_(ComponentModel.context, ComponentModel.name).in_(context_names)
        )
        with self.session_factory() as session:
            models = session.execute(stmt).scalars().all()
            items = [ComponentMapper.to_dto(m) for m in models]
            return items

    @override
    def find_by_ids(
        self, ids: Collection[ComponentId]
    ) -> dict[ComponentId, ComponentDto]:
        if not ids:
            return {}
        unique_ids: set[str] = {str(i) for i in ids}
        stmt = select(ComponentModel).where(ComponentModel.id.in_(unique_ids))
        with self.session_factory() as session:
            models = session.execute(stmt).scalars().all()
            return {
                ComponentId.reconstitute(m.id): ComponentMapper.to_dto(m)
                for m in models
            }
