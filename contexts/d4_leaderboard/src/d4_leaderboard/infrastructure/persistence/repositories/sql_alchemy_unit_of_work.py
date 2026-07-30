import logging
from dataclasses import dataclass
from typing import override
from d4_leaderboard.application.ports.repo_provider import RepoProvider
from d4_leaderboard.domain.repositories.entry_repository import EntryRepository
from d4_leaderboard.infrastructure.persistence.repositories.sql_alchemy_entry_repository import (
    SqlAlchemyEntryRepository,
)
from foundation.persistence.ports.session_manager import SessionManager
from foundation.persistence.sessions.sqlalchemy_session import SqlAlchemySession

logger = logging.getLogger(__name__)


@dataclass
class SqlAlchemyUnitOfWork(SessionManager[SqlAlchemySession], RepoProvider):
    @property
    @override
    def entries(self) -> EntryRepository:
        return SqlAlchemyEntryRepository(self.session)
