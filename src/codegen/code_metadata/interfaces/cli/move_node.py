from typing import Annotated
import typer
from dependency_injector.wiring import Provide
from dependency_injector.wiring import inject
from rich.console import Console
from codegen.code_metadata.application.commands.move_node import MoveNodeCommand
from codegen.code_metadata.domain.core.fqn import Fqn
from codegen.code_metadata.infrastructure.message_bus import MessageBus

console = Console()


@inject
def _move_node(
    cmd: MoveNodeCommand,
    message_bus: MessageBus = Provide["code_metadata_container.message_bus"],
) -> None:
    message_bus.handle(cmd)


def move_node(
    fqn: Annotated[
        str, typer.Argument(help="The FQN of the node to move")
    ],
    target_fqn: Annotated[
        str,
        typer.Argument()
    ],
) -> None:
    """move an unused CodeNode and its orphaned module from the graph."""
    cmd = MoveNodeCommand(
        node_fqn=Fqn(fqn),
        target_fqn=Fqn(target_fqn)
    )
    _move_node(cmd)
