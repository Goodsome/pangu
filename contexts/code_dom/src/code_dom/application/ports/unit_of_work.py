from collections.abc import Iterator
import logging
from abc import ABC
from abc import abstractmethod
from typing import override
from code_dom.domain.repositories.codebase_repository import CodebaseRepository
from code_dom.domain.repositories.document_repository import DocumentRepository
from foundation.persistence.ports.base_unit_of_work import BaseUnitOfWork
from foundation.building_blocks.event import DomainEvent

logger = logging.getLogger(__name__)


class UnitOfWork(BaseUnitOfWork, ABC):
    @property
    @abstractmethod
    def codebases(self) -> CodebaseRepository:
        pass

    @property
    @abstractmethod
    def documents(self) -> DocumentRepository:
        pass

    @override
    def collect_events(self) -> Iterator[DomainEvent]:
        yield from self.codebases.collect_events()
        yield from self.documents.collect_events()
