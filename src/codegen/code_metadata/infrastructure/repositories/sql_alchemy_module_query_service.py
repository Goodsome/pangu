from dataclasses import dataclass
from typing import override
from sqlalchemy import ColumnElement
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from codegen.code_metadata.application.dtos.module_dto import ModuleDto
from codegen.code_metadata.application.dtos.module_filter import ModuleFilter
from codegen.code_metadata.application.ports.module_query_service import (
    ModuleQueryService,
)
from codegen.code_metadata.infrastructure.mappers.module_mapper import ModuleMapper
from codegen.code_metadata.infrastructure.orm_models.module_model import ModuleModel
from codegen.shared.application.dtos.page import Page
from codegen.shared.application.dtos.page_query import PageQuery


@dataclass
class SqlAlchemyModuleQueryService(ModuleQueryService):
    session_factory: sessionmaker[Session]

    @override
    def find_page(self, page_query: PageQuery[ModuleFilter]) -> Page[ModuleDto]:
        conditions = self._build_conditions(page_query.condition)
        stmt = select(ModuleModel).where(*conditions)
        with self.session_factory() as session:
            total = (
                session.scalar(
                    select(func.count()).select_from(ModuleModel).where(*conditions)
                )
                or 0
            )
            if page_query.current and page_query.size:
                offset = (page_query.current - 1) * page_query.size
                stmt = stmt.offset(offset=offset).limit(page_query.size)
            models = session.execute(stmt).scalars().all()
        items = [ModuleMapper.to_dto(m) for m in models]
        return Page(
            items=items, total=total, current=page_query.current, size=page_query.size
        )

    @override
    def find_by_filter(self, filter: ModuleFilter) -> list[ModuleDto]:
        conditions = self._build_conditions(filter)
        stmt = select(ModuleModel).where(*conditions)
        with self.session_factory() as session:
            models = session.execute(stmt).scalars().all()
        return [ModuleMapper.to_dto(m) for m in models]

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
