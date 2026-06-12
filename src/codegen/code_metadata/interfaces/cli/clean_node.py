from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject
from rich.console import Console

from codegen.code_metadata.application.commands.clean_node import (
    CleanNodeCommand,
)
from codegen.code_metadata.infrastructure.message_bus import MessageBus

console = Console()


@inject
def _clean_node(
    cmd: CleanNodeCommand,
    message_bus: MessageBus = Provide["code_metadata_container.message_bus"],
) -> None:
    message_bus.handle(cmd)


def clean_node(
    fqn: Annotated[str, typer.Argument(help="The FQN of the node to clean")],
) -> None:
    """Clean an unused CodeNode and its orphaned module from the graph."""
    cmd = CleanNodeCommand(fqn=fqn)
    _clean_node(cmd)
    console.print(f"[green]Node '{fqn}' cleaned successfully.[/green]")
