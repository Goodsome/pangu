from pathlib import Path
import subprocess
import sys
from typing import override
from codegen.code_dom.domain.ports.code_formatter import CodeFormatter


class RuffCodeFormatter(CodeFormatter):

    @override
    def format_code(self, code: str) -> str:
        try:
            result = subprocess.run(
                [sys.executable, "-m", "ruff", "format", "-"],
                input=code,           
                capture_output=True, 
                text=True,           
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise e

    @override
    def format_path(self, path: Path) -> None:
        try:
            subprocess.run(
                [sys.executable, "-m", "ruff", "format", str(path)],
                capture_output=True,
                text=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            raise e