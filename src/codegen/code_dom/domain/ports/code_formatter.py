from abc import ABC
from abc import abstractmethod


class CodeFormatter(ABC):
    """Formats Python source code."""

    @abstractmethod
    def format_code(self, code: str) -> str: ...
