from typing import Annotated
from dependency_injector.wiring import Provide, inject
from rich.console import Console
from typer import Argument
from architecture.application.commands.rename_module import RenameModuleCommand
from foundation.common_types.fqns.fqn import ModuleFqn
from architecture.infrastructure.message_bus import MessageBus

console = Console()


@inject
def _rename_module(
    cmd: RenameModuleCommand,
    message_bus: MessageBus = Provide["architecture_container.message_bus"],
):
    message_bus.handle(cmd)


def rename_module(
    module_fqn: Annotated[
        str, Argument(help="Module FQN to rename (要重命名的模块 FQN)")
    ],
    new_name: Annotated[str, Argument(help="New name for the module (模块的新名称)")],
) -> None:
    try:
        cmd = RenameModuleCommand(module_fqn=ModuleFqn(module_fqn), new_name=new_name)
        _rename_module(cmd)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
