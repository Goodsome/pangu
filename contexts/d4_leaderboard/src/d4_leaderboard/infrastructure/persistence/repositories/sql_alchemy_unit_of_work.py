from dataclasses import dataclass, field
from typing import override
from foundation.persistence.ports.session_manager import AsyncSessionManager
from foundation.persistence.sessions.sqlalchemy_session import AsyncSqlAlchemySession
from d4_leaderboard.domain.repositories.entry_repository import EntryRepository
from d4_leaderboard.application.ports.repo_provider import RepoProvider
from d4_leaderboard.infrastructure.persistence.repositories.sql_alchemy_entry_repository import (
    SqlAlchemyEntryRepository,
)


@dataclass
class SqlAlchemyUnitOfWork(AsyncSessionManager[AsyncSqlAlchemySession], RepoProvider):
    """d4_leaderboard SQLAlchemy Unit of Work 实现。

    所有 repository 属性均使用懒加载缓存，确保同一 UoW 生命周期内
    返回同一实例，以保证 `_seens` 集合（领域事件收集）不丢失。
    """

    _entries: SqlAlchemyEntryRepository | None = field(default=None, init=False)

    @property
    @override
    def entries(self) -> EntryRepository:
        if self._entries is None:
            self._entries = SqlAlchemyEntryRepository(self.session)
        return self._entries
