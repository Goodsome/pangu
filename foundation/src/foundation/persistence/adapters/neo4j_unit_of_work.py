import json
import logging
from dataclasses import dataclass, field
from types import TracebackType
from typing import Any, Protocol, Self, override
from foundation.persistence.sessions.neo4j_session import Neo4jSession
from neo4j import Driver
from foundation.building_blocks.event import IntegrationEvent
from foundation.persistence.ports.repository import Repository
from foundation.persistence.ports.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)


class RepositoryFactory[T: Repository[Any, Any]](Protocol):
    def __call__(self, session: Neo4jSession) -> T: ...


@dataclass
class MemgraphUnitOfWork[T_Repo: Repository[Any, Any]](UnitOfWork[T_Repo]):
    driver: Driver
    repository_factory: RepositoryFactory[T_Repo]
    _session: Neo4jSession | None = field(default=None, init=False)
    _repository: T_Repo | None = field(default=None, init=False)

    @override
    def __enter__(self) -> Self:
        self._session = Neo4jSession(driver=self.driver)
        self._repository = self.repository_factory(self._session)
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
        else:
            pass
        if self._session:
            self._session.close()
            self._session = None
        self._repository = None

    @property
    @override
    def repository(self) -> T_Repo:
        if not self._repository:
            raise RuntimeError("Unit of work is not active. Use 'with uow:' block.")
        return self._repository

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
