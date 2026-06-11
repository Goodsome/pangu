from typing import Annotated
import typer
from dependency_injector.wiring import Provide
from dependency_injector.wiring import inject
from rich.console import Console
from codegen.code_metadata.application.commands.ingest_project import IngestProject
from codegen.code_metadata.application.dtos.ingest_project_command import (
    IngestProjectCommand,
)

console = Console()


@inject
def _ingest_project(
    cmd: IngestProjectCommand,
    use_case: IngestProject = Provide["code_metadata_container.ingest_project"],
) -> None:
    result = use_case.execute(cmd)
    console.print(
        f"[green]Ingest complete:[/green] {result.nodes_created} nodes synced, {result.edges_created} edges recorded, {result.nodes_deleted} stale nodes removed."
    )


def ingest_project(
    prefix: Annotated[
        str | None,
        typer.Option(
            "--prefix", "-p",
            help="The prefix of the bounded context to ingest, e.g. src/codegen/code_metadata"
        ),
    ]=None,
) -> None:
    """Scan a bounded context's directory tree into the CodeNode graph."""
    cmd = IngestProjectCommand(prefix=prefix)
    _ingest_project(cmd)
