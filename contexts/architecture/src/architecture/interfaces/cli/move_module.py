from typing import Annotated
from dependency_injector.wiring import Provide, inject
from rich.console import Console
from typer import Argument
from architecture.application.commands.move_module import MoveModuleCommand
from foundation.common_types.fqns.fqn import ModuleFqn
from architecture.infrastructure.message_bus import MessageBus

console = Console()


@inject
def _move_module(
    cmd: MoveModuleCommand,
    message_bus: MessageBus = Provide["architecture_container.message_bus"],
):
    message_bus.handle(cmd)


def move_module(
    module_fqn: Annotated[str, Argument(help="Module FQN to move (要移动的模块 FQN)")],
    target_fqn: Annotated[
        str, Argument(help="Target parent module FQN (目标父模块 FQN)")
    ],
) -> None:
    try:
        cmd = MoveModuleCommand(
            module_fqn=ModuleFqn(module_fqn), target_fqn=ModuleFqn(target_fqn)
        )
        _move_module(cmd)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
