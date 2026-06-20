from abc import ABC, abstractmethod
from pathlib import Path

from architecture.domain.value_objects.parsed_module import ParsedModule



class CodeScanner(ABC):

    @abstractmethod
    def scan_directory(self, root_path: Path) -> list[ParsedModule]:
        ...