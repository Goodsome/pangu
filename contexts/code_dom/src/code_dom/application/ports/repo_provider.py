import logging
from abc import ABC, abstractmethod
from collections.abc import Iterator
from code_dom.domain.repositories.codebase_repository import CodebaseRepository
from code_dom.domain.repositories.document_repository import DocumentRepository
from foundation.building_blocks.event import DomainEvent

logger = logging.getLogger(__name__)


class RepoProvider(ABC):
    @property
    @abstractmethod
    def codebases(self) -> CodebaseRepository:
        pass

    @property
    @abstractmethod
    def documents(self) -> DocumentRepository:
        pass

    def collect_events(self) -> Iterator[DomainEvent]:
        yield from self.codebases.collect_events()
        yield from self.documents.collect_events()
