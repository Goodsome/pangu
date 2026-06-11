from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject
from rich.console import Console

from codegen.code_metadata.application.commands.clean_node import (
    CleanNodeCommand,
    CleanNodeHandler,
)

console = Console()


@inject
def _clean_node(
    cmd: CleanNodeCommand,
    handler: CleanNodeHandler = Provide["code_metadata_container.clean_node"],
) -> None:
    handler.execute(cmd)


def clean_node(
    fqn: Annotated[str, typer.Argument(help="The FQN of the node to clean")],
) -> None:
    """Clean an unused CodeNode and its orphaned module from the graph."""
    cmd = CleanNodeCommand(fqn=fqn)
    try:
        _clean_node(cmd)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    console.print(f"[green]Node '{fqn}' cleaned successfully.[/green]")
