from abc import ABC
from abc import abstractmethod
from pathlib import Path
from typing import Iterator


class FileSystemPort(ABC):
    """Port for interacting with the file system."""

    @abstractmethod
    def read_file(self, path: Path) -> str: ...

    @abstractmethod
    def write_file(self, path: Path, content: str, overwrite: bool = False) -> bool:
        """Writes content to file. Returns True if written, False if skipped (due to overwrite=False)."""
        ...

    @abstractmethod
    def list_directory_recursively(
        self, path: Path, pattern: str = "*", ignore_dirs: set[str] | None = None
    ) -> Iterator[Path]: ...

    @abstractmethod
    def list_directory_flat(self, path: Path) -> Iterator[Path]: ...

    @abstractmethod
    def is_directory(self, path: Path) -> bool: ...

    @abstractmethod
    def is_file(self, path: Path) -> bool: ...

    @abstractmethod
    def exists(self, path: Path) -> bool: ...
