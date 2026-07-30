from abc import ABC, abstractmethod
from collections.abc import Collection
from pathlib import Path
from code_dom.domain.aggregates.code_document import CodeDocument
from foundation.persistence.ports.repository import Repository


class DocumentRepository(Repository[CodeDocument, Path], ABC):
    @abstractmethod
    def delete_all(self, ids: Collection[Path]) -> None: ...
