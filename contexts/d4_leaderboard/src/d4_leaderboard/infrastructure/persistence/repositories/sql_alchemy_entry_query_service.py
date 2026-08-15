from dataclasses import dataclass
from typing import override

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from d4_leaderboard.application.dtos.entry_dto import EntryDto
from d4_leaderboard.application.dtos.entry_filter import EntryFilter
from d4_leaderboard.application.ports.entry_query_service import EntryQueryService
from d4_leaderboard.domain.identities.entry_id import EntryId
from d4_leaderboard.infrastructure.persistence.mappers.entry_mapper import (
    entry_model_to_entry_dto,
)
from d4_leaderboard.infrastructure.persistence.models.entry_model import EntryModel
from foundation.common_types.page import Page, PageQuery


@dataclass
class SqlAlchemyEntryQueryService(EntryQueryService):
    session_factory: async_sessionmaker[AsyncSession]

    @override
    async def get(self, id: EntryId) -> EntryDto:
        async with self.session_factory() as session:
            model = await session.get(EntryModel, id.value)
            if not model:
                raise ValueError(f"Entry {id} not found")
            return entry_model_to_entry_dto(model)

    @override
    async def find_by_query(self, query: PageQuery[EntryFilter]) -> Page[EntryDto]:
        async with self.session_factory() as session:
            conditions = []
            if query.condition.player_class is not None:
                conditions.append(
                    EntryModel.player_class == query.condition.player_class
                )

            count_stmt = select(func.count()).select_from(EntryModel).where(*conditions)
            total_res = await session.execute(count_stmt)
            total: int = total_res.scalar_one() or 0

            # 榜单固定语义：层数高者靠前，同层用时短者靠前，仍相同按时间早者靠前
            stmt = (
                select(EntryModel)
                .where(*conditions)
                .order_by(
                    EntryModel.tier.desc(),
                    EntryModel.duration_ms.asc(),
                    EntryModel.occurred_at.asc(),
                )
            )
            if query.size is not None and query.size > 0:
                offset = (query.current - 1) * query.size
                stmt = stmt.offset(offset).limit(query.size)

            res = await session.execute(stmt)
            models = res.scalars().all()

            items = [entry_model_to_entry_dto(m) for m in models]

            return Page[EntryDto](
                items=items,
                total=total,
                current=query.current,
                size=query.size,
            )
