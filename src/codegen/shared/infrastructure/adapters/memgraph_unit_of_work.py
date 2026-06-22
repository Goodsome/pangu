import logging
import json
from dataclasses import dataclass, field
from types import TracebackType
from typing import Any, Protocol, override, Self
from neo4j import Driver, Session, Transaction
from codegen.shared.application.ports.unit_of_work import UnitOfWork
from foundation.building_blocks.event import IntegrationEvent
from foundation.persistence.repository import Repository

logger = logging.getLogger(__name__)


class RepositoryFactory[T: Repository[Any, Any]](Protocol):
    def __call__(self, transaction: Transaction) -> T: ...


@dataclass
class MemgraphUnitOfWork[T_Repo: Repository[Any, Any]](UnitOfWork[T_Repo]):
    driver: Driver
    repository_factory: RepositoryFactory[T_Repo]
    session: Session | None = field(default=None, init=False)
    transaction: Transaction | None = field(default=None, init=False)
    _repository: T_Repo | None = field(default=None, init=False)

    @override
    def __enter__(self) -> Self:
        self.session = self.driver.session()
        self.transaction = self.session.begin_transaction()
        self._repository = self.repository_factory(self.transaction)
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
            logger.error(f"Transaction rolled back due to error: {exc_val}")
        else:
            pass
        if self.transaction:
            self.transaction.close()
            self.transaction = None
        if self.session:
            self.session.close()
            self.session = None
        self._repository = None

    @property
    @override
    def repository(self) -> T_Repo:
        if not self._repository:
            raise RuntimeError("Unit of work is not active. Use 'with uow:' block.")
        return self._repository

    @override
    def commit(self):
        if self.transaction:
            self.transaction.commit()

    @override
    def rollback(self):
        if self.transaction:
            self.transaction.rollback()

    @override
    def save_outbox_message(self, message: IntegrationEvent):
        if not self.transaction:
            raise RuntimeError("Transaction is not active")
        payload = message.model_dump(mode="json")
        event_type = type(message).__name__
        query = "\n        CREATE (o:OutboxMessage {\n            event_type: $event_type,\n            payload: $payload,\n            created_at: timestamp()\n        })\n        "
        self.transaction.run(query, event_type=event_type, payload=json.dumps(payload))
