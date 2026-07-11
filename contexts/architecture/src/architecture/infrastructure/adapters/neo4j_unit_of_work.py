from dataclasses import dataclass, field
from types import TracebackType
from typing import Self, override
from architecture.application.ports.unit_of_work import UnitOfWork
from architecture.domain.repositories.file_module_repository import FileModuleRepository
from architecture.domain.repositories.package_module_repository import (
    PackageModuleRepository,
)
from architecture.infrastructure.repositories.neo4j_file_module_repository import (
    Neo4jFileModuleRepository,
)
from architecture.infrastructure.repositories.neo4j_package_module_repository import (
    Neo4jPackageModuleRepository,
)
from foundation.building_blocks.event import IntegrationEvent
from foundation.persistence.sessions.neo4j_session import Neo4jSession
from neo4j import Driver
import json


@dataclass
class Neo4jUnitOfWork(UnitOfWork):
    driver: Driver
    _session: Neo4jSession | None = field(default=None, init=False)
    _file_module_repo: Neo4jFileModuleRepository | None = field(
        default=None, init=False
    )
    _package_module_repo: Neo4jPackageModuleRepository | None = field(
        default=None, init=False
    )

    @override
    def __enter__(self) -> Self:
        self._session = Neo4jSession(driver=self.driver)
        self._file_module_repo = Neo4jFileModuleRepository(session=self._session)
        self._package_module_repo = Neo4jPackageModuleRepository(session=self._session)
        return self

    @override
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        if exc_type is not None:
            self.rollback()
        if self._session:
            self._session.close()
            self._session = None
        self._file_module_repo = None
        self._package_module_repo = None

    @property
    @override
    def file_modules(self) -> FileModuleRepository:
        if not self._file_module_repo:
            raise RuntimeError("Unit of work is not active. Use 'with uow:' block.")
        return self._file_module_repo

    @property
    @override
    def packages(self) -> PackageModuleRepository:
        if not self._package_module_repo:
            raise RuntimeError("Unit of work is not active. Use 'with uow:' block.")
        return self._package_module_repo

    @override
    def commit(self):
        if self._session:
            self._session.commit()

    @override
    def rollback(self):
        if self._session:
            self._session.rollback()

    @override
    def save_outbox_message(self, message: IntegrationEvent):
        if not self._session:
            raise RuntimeError("Transaction is not active")
        payload = message.model_dump(mode="json")
        event_type = type(message).__name__
        query = "CREATE (o:OutboxMessage { event_type: $event_type, payload: $payload, created_at: timestamp() })"
        self._session.execute(query, event_type=event_type, payload=json.dumps(payload))
