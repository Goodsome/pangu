from dataclasses import dataclass
from pathlib import Path
from typing import Iterator
from codegen.shared.domain.ports.file_system_port import FileSystemPort


@dataclass
class OSFileSystem(FileSystemPort):
    """OS file system adapter for reading/writing files."""

    root: Path
    encoding: str = "utf-8"

    def read_file(self, path: Path) -> str:
        full_path = self.root / path
        return full_path.read_text(encoding=self.encoding)

    def write_file(self, path: Path, content: str, overwrite: bool = False) -> bool:
        """Writes content to file. Returns True if written, False if skipped (due to overwrite=False)."""
        full_path = self.root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        if full_path.exists() and (not overwrite):
            return False
        _ = full_path.write_text(content, encoding=self.encoding)
        return True

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

    def list_directory_flat(self, path: Path) -> Iterator[Path]:
        full_path = self.root / path
        for entry in full_path.iterdir():
            yield entry.relative_to(self.root)

    def is_directory(self, path: Path) -> bool:
        return (self.root / path).is_dir()

    def is_file(self, path: Path) -> bool:
        return (self.root / path).is_file()

    def exists(self, path: Path) -> bool:
        return (self.root / path).exists()
