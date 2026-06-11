from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from codegen.code_metadata.domain.core.fqn import Fqn


@dataclass
class FqnFactory:
    SOURCE_ROOTS: ClassVar[list[Path]] = [Path("src")]

    def build_module_fqn(self, path: Path) -> Fqn:
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
            return Fqn(".".join(logical_path.parent.parts))
        return Fqn(".".join(logical_path.with_suffix("").parts))
