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


@inject
def _get_file_document(
    query: GetFileDocumentQuery,
    handler: GetFileDocumentHandler = Provide["code_dom_container.get_file_document"],
) -> GetFileDocumentResult:
    return handler.handle(query)


def get_file_document(
    file_path: Annotated[Path, typer.Argument(help="Path to the Python file to parse")],
) -> None:
    """Parse a single Python file and display its AST document."""
    query = GetFileDocumentQuery(file_path=file_path)
    try:
        result = _get_file_document(query)
    except FileNotFoundError:
        console.print(f"[red]Error: file not found: {file_path}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error parsing file: {e}[/red]")
        raise typer.Exit(1)
    doc = result.code_document
    console.print(f"[bold]File:[/bold] {doc.physical_path}")
    console.print(f"[bold]Statements:[/bold] {len(doc.body)}")
    console.print()
    for stmt in doc.body:
        console.print(f"  {stmt}")
