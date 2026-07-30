from foundation.persistence.sessions.sqlalchemy_session import AsyncSqlAlchemySession
from d4_leaderboard.domain.aggregates.entry import Entry
from d4_leaderboard.domain.identities.entry_id import EntryId
from d4_leaderboard.infrastructure.persistence.models.entry_model import EntryModel
from d4_leaderboard.domain.repositories.entry_repository import EntryRepository
from dataclasses import dataclass
from d4_leaderboard.infrastructure.persistence.mappers.entry_mapper import (
    entry_entity_to_model,
)
from d4_leaderboard.infrastructure.persistence.mappers.entry_mapper import (
    entry_model_to_entity,
)
from typing import override


@dataclass
class SqlAlchemyEntryRepository(EntryRepository):
    session: AsyncSqlAlchemySession

    @override
    async def _add(self, aggregate: Entry) -> None:
        model = entry_entity_to_model(aggregate)
        self.session.add(model)

    @override
    async def _add_all(self, aggregates: list[Entry]) -> None:
        models = [entry_entity_to_model(a) for a in aggregates]
        self.session.add_all(models)

    @override
    async def _get(self, id: EntryId) -> Entry:
        model = await self.session.get(EntryModel, id.value)
        if not model:
            raise ValueError(f"Entry {id} not found")
        return entry_model_to_entity(model)

    @override
    async def _save(self, aggregate: Entry) -> None:
        model = entry_entity_to_model(aggregate)
        await self.session.merge(model)

    @override
    async def _save_all(self, aggregates: list[Entry]) -> None:
        for aggregate in aggregates:
            await self._save(aggregate)

    @override
    async def _delete(self, aggregate: Entry) -> None:
        model = await self.session.get(EntryModel, aggregate.id.value)
        if model:
            await self.session.delete(model)
