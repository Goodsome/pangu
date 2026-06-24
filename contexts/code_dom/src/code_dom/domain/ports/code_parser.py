from abc import ABC
from abc import abstractmethod
from pathlib import Path
from code_dom.domain.aggregates.code_document import CodeDocument


class CodeParser(ABC):
    @abstractmethod
    def parse_file(self, path: Path) -> CodeDocument: ...

    @abstractmethod
    def parse_directory(self, path: Path) -> list[CodeDocument]: ...
