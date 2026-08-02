import logging
from abc import ABC, abstractmethod
from code_dom.domain.repositories.codebase_repository import CodebaseRepository
from code_dom.domain.repositories.document_repository import DocumentRepository

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
