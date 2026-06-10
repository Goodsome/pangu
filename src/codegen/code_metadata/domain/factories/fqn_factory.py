from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar


@dataclass
class FqnFactory:
    SOURCE_ROOTS: ClassVar[list[Path]] = [Path("src")]

    def build_dir_fqn(self, path: Path) -> str:
        """目录 FQN：相对路径/，以 / 结尾。根目录为 /。"""
        if path == Path("."):
            return "/"
        return f"{path.as_posix()}/"

    def build_file_fqn(self, path: Path) -> str:
        """文件 FQN：相对文件路径。"""
        return path.as_posix()

    def build_module_fqn(self, path: Path) -> str:
        """模块 FQN：将路径分隔符替换为 '.'，去除后缀。

        __init__.py 映射到其所在目录的包名(如 src/foo/__init__.py → src.foo),
        其余文件映射到模块路径(如 src/foo/bar.py → src.foo.bar)。
        """
        logical_path = path
        for src_root in self.SOURCE_ROOTS:
            try:
                logical_path = path.relative_to(src_root)
                break
            except ValueError:
                continue
        if logical_path.name == "__init__.py":
            return ".".join(logical_path.parent.parts)
        return ".".join(logical_path.with_suffix("").parts)
