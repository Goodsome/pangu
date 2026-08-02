from dataclasses import dataclass, field
from typing import override
from architecture.application.ports.repo_provider import RepoProvider
from architecture.domain.repositories.file_module_repository import (
    FileModuleRepository,
)
from architecture.domain.repositories.package_module_repository import (
    PackageModuleRepository,
)
from architecture.infrastructure.repositories.neo4j_file_module_repository import (
    Neo4jFileModuleRepository,
)
from architecture.infrastructure.repositories.neo4j_package_module_repository import (
    Neo4jPackageModuleRepository,
)
from foundation.persistence.ports.outbox_repository import OutboxRepository
from foundation.persistence.ports.session_manager import SessionManager
from foundation.persistence.repositories.neo4j_outbox_repository import (
    Neo4jOutboxRepository,
)
from foundation.persistence.sessions.neo4j_session import Neo4jSession


@dataclass
class Neo4jUnitOfWork(SessionManager[Neo4jSession], RepoProvider):
    """Neo4j Unit of Work 实现。

    注意：所有 repository 属性均使用懒加载缓存，确保同一个 UoW 生命周期内
    返回同一个实例，以保证 `_seens` 集合（用于领域事件收集）不会丢失。
    """

    _file_modules: Neo4jFileModuleRepository | None = field(default=None, init=False)
    _packages: Neo4jPackageModuleRepository | None = field(default=None, init=False)
    _outbox: Neo4jOutboxRepository | None = field(default=None, init=False)

    @property
    @override
    def file_modules(self) -> FileModuleRepository:
        if self._file_modules is None:
            self._file_modules = Neo4jFileModuleRepository(session=self.session)
        return self._file_modules

    @property
    @override
    def packages(self) -> PackageModuleRepository:
        if self._packages is None:
            self._packages = Neo4jPackageModuleRepository(session=self.session)
        return self._packages

    @property
    @override
    def outbox(self) -> OutboxRepository:
        if self._outbox is None:
            self._outbox = Neo4jOutboxRepository(session=self.session)
        return self._outbox
