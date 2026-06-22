from abc import ABC
from abc import abstractmethod
from pathlib import Path


class CodeFormatter(ABC):
    """Formats Python source code."""

    @abstractmethod
    def format_code(self, code: str) -> str: ...

    @abstractmethod
    def format_path(self, path: Path): ...