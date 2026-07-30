from foundation.persistence.ports.session_manager import AsyncSessionManager
from foundation.persistence.sessions.sqlalchemy_session import AsyncSqlAlchemySession
from d4_leaderboard.domain.repositories.entry_repository import EntryRepository
from d4_leaderboard.application.ports.repo_provider import RepoProvider
from d4_leaderboard.infrastructure.persistence.repositories.sql_alchemy_entry_repository import (
    SqlAlchemyEntryRepository,
)
from dataclasses import dataclass
from typing import override


@dataclass
class SqlAlchemyUnitOfWork(AsyncSessionManager[AsyncSqlAlchemySession], RepoProvider):
    @property
    @override
    def entries(self) -> EntryRepository:
        return SqlAlchemyEntryRepository(self.session)
