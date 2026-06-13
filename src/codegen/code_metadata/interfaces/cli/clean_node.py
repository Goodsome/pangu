from typing import Annotated

import typer
from dependency_injector.wiring import Provide, inject
from rich.console import Console

from codegen.code_metadata.application.commands.clean_node import (
    CleanNodeCommand,
)
from codegen.code_metadata.application.commands.clean_unused_nodes import (
    CleanUnusedNodesCommand,
)
from codegen.code_metadata.domain.enums.code_node_kind import CodeNodeKind
from codegen.code_metadata.infrastructure.message_bus import MessageBus

console = Console()


@inject
def _clean_node(
    cmd: CleanNodeCommand | CleanUnusedNodesCommand,
    message_bus: MessageBus = Provide["code_metadata_container.message_bus"],
) -> None:
    message_bus.handle(cmd)


def clean_node(
    fqn: Annotated[
        str | None, typer.Option("--fqn", "-f", help="The FQN of the node to clean")
    ] = None,
) -> None:
    """Clean an unused CodeNode and its orphaned module from the graph."""
    if fqn:
        cmd = CleanNodeCommand(fqn=fqn)
    else:
        cmd = CleanUnusedNodesCommand(kind=CodeNodeKind.CLASS)
    _clean_node(cmd)
    console.print(f"[green]Node '{fqn}' cleaned successfully.[/green]")
