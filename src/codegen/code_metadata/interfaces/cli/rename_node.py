from typing import Annotated

import typer
from dependency_injector.wiring import Provide
from dependency_injector.wiring import inject
from rich.console import Console

from codegen.code_metadata.application.commands.rename_node import RenameNodeCommand
from codegen.code_metadata.domain.core.fqn import Fqn
from codegen.code_metadata.infrastructure.message_bus import MessageBus

console = Console()


@inject
def _rename_node(
    cmd: RenameNodeCommand,
    message_bus: MessageBus = Provide["code_metadata_container.message_bus"],
) -> None:
    message_bus.handle(cmd)


def rename_node(
    fqn: Annotated[str, typer.Argument(help="The FQN of the node to rename")],
    name: Annotated[str, typer.Argument(help="The new name")],
) -> None:
    """Rename a CodeNode and batch-update all descendant FQNs."""
    cmd = RenameNodeCommand(fqn=Fqn(fqn), name=name)
    _rename_node(cmd)
