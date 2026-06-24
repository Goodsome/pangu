import logging
import subprocess
import sys
from typing import override
from pathlib import Path
from code_dom.domain.ports.code_formatter import CodeFormatter

logger = logging.getLogger(__name__)


class RuffCodeFormatter(CodeFormatter):
    @override
    def format_code(self, code: str) -> str:
        try:
            result = subprocess.run(
                [sys.executable, "-m", "ruff", "format", "-"],
                input=code,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise e

    @override
    def format_path(self, path: Path) -> None:
        try:
            result = subprocess.run(
                [sys.executable, "-m", "ruff", "format", str(path)],
                capture_output=True,
                text=True,
                check=True,
            )
            logger.info(f"Formatted path {path}: {result.stdout}")
        except subprocess.CalledProcessError as e:
            logger.error(
                f"Failed to format path {path}.\n"
                + f"Exit code: {e.returncode}\n"
                + f"Stdout: {e.stdout}\n"
                + f"Stderr: {e.stderr}"
            )
            raise e
