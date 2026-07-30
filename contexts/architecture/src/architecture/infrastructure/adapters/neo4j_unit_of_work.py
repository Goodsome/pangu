from dataclasses import dataclass
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
    @property
    @override
    def file_modules(self) -> FileModuleRepository:
        return Neo4jFileModuleRepository(session=self.session)

    @property
    @override
    def packages(self) -> PackageModuleRepository:
        return Neo4jPackageModuleRepository(session=self.session)

    @property
    @override
    def outbox(self) -> OutboxRepository:
        return Neo4jOutboxRepository(session=self.session)
