import logging
from dataclasses import dataclass
from types import TracebackType
from typing import Self, override
from codegen.code_dom.application.ports.unit_of_work import UnitOfWork
from codegen.code_dom.domain.repositories.codebase_repository import CodebaseRepository
from codegen.code_dom.domain.repositories.document_repository import DocumentRepository
from foundation.building_blocks.event import IntegrationEvent
from codegen.shared.infrastructure.orm_models.outbox_message_module import (
    OutboxMessageModel,
)

logger = logging.getLogger(__name__)


@dataclass
class FileSystemUnitOfWork(UnitOfWork):
    codebase_repository: CodebaseRepository | None
    document_repository: DocumentRepository | None
    session: None = None

    @override
    def __enter__(self) -> Self:
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
        if self.session:
            self.session.close()
            self.session = None
            self.codebase_repository = None

    @property
    @override
    def codebases(self) -> CodebaseRepository:
        if not self.codebase_repository:
            raise RuntimeError("Unit of work is not active. Use 'with uow:' block.")
        return self.codebase_repository

    @property
    @override
    def documents(self) -> DocumentRepository:
        if not self.document_repository:
            raise RuntimeError("Unit of work is not active. Use 'with uow:' block.")
        return self.document_repository

    @override
    def commit(self):
        if self.session:
            self.session.commit()

    @override
    def rollback(self):
        if self.session:
            self.session.rollback()

    @override
    def save_outbox_message(self, message: IntegrationEvent):
        if not self.session:
            raise RuntimeError("Session is not active")
        payload = message.model_dump(mode="json")
        record = OutboxMessageModel(event_type=type(message).__name__, payload=payload)
        self.session.add(record)
