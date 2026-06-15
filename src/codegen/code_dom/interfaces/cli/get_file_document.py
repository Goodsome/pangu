from pathlib import Path
from typing import Annotated
import typer
from dependency_injector.wiring import Provide
from dependency_injector.wiring import inject
from rich.console import Console
from codegen.code_dom.application.queries.get_file_document import (
    GetFileDocumentHandler,
)
from codegen.code_dom.application.queries.get_file_document import GetFileDocumentQuery
from codegen.code_dom.application.queries.get_file_document import GetFileDocumentResult

console = Console()
