import logging
import shutil
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import override
from foundation.system.file_system_port import FileSystemPort

logger = logging.getLogger(__name__)


@dataclass
class OSFileSystem(FileSystemPort):
    """OS file system adapter for reading/writing files."""

    "OS file system adapter for reading/writing files."
    root: Path
    encoding: str = "utf-8"

    @override
    def read_file(self, path: Path) -> str:
        full_path = self.root / path
        return full_path.read_text(encoding=self.encoding)

    @override
    def write_file(self, path: Path, content: str, overwrite: bool = False) -> bool:
        """Writes content to file. Returns True if written, False if skipped (due to overwrite=False)."""
        full_path = self.root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        if full_path.exists() and (not overwrite):
            return False
        _ = full_path.write_text(content, encoding=self.encoding)
        return True

    @override
    def list_directory_recursively(
        self, path: Path, pattern: str = "*", ignore_dirs: set[str] | None = None
    ) -> Iterator[Path]:
        if ignore_dirs is None:
            ignore_dirs = {"__pycache__", ".git", ".venv", "node_modules"}
        target_path = self.root / path
        for root_dir, dir_names, file_names in target_path.walk():
            dir_names[:] = [d for d in dir_names if d not in ignore_dirs]
            for file_name in file_names:
                file_path = root_dir / file_name
                rp = file_path.relative_to(self.root)
                if rp.match(pattern):
                    yield rp

    @override
    def list_directory_flat(self, path: Path) -> Iterator[Path]:
        full_path = self.root / path
        for entry in full_path.iterdir():
            yield entry.relative_to(self.root)

    @override
    def is_directory(self, path: Path) -> bool:
        return (self.root / path).is_dir()

    @override
    def is_file(self, path: Path) -> bool:
        return (self.root / path).is_file()

    @override
    def exists(self, path: Path) -> bool:
        return (self.root / path).exists()

    @override
    def delete_file(self, path: Path) -> bool:
        full_path = self.root / path
        if not full_path.is_file():
            logger.warning(f"full_path={full_path!r} is not fille, skip")
            return False
        full_path.unlink()
        return True

    @override
    def delete_directory(self, path: Path) -> bool:
        full_path = self.root / path
        if not full_path.is_dir():
            logger.warning(f"full_path={full_path!r} is not a directory, skip")
            return False
        shutil.rmtree(full_path)
        return True

    @override
    def move(self, path: Path, target_path: Path):
        full_path = self.root / path
        full_target_path = self.root / target_path
        full_target_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.rename(full_target_path)
