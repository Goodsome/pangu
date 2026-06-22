from pathlib import Path
from typing import override
import black
from codegen.code_dom.domain.ports.code_formatter import CodeFormatter


class BlackCodeFormatter(CodeFormatter):

    @override
    def format_code(self, code: str) -> str:
        return black.format_str(code, mode=black.Mode())

    @override
    def format_path(self, path: Path) -> None:
        raise NotImplementedError(f"{path}")
