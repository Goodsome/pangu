from typing import Annotated
from dependency_injector.wiring import Provide, inject
from typer import Argument
from architecture.application.commands.remove_module import RemoveModuleCommand
from foundation.common_types.fqns.fqn import ModuleFqn
from architecture.infrastructure.message_bus import MessageBus


@inject
def _remove_module(
    cmd: RemoveModuleCommand,
    message_bus: MessageBus = Provide["architecture_container.message_bus"],
):
    message_bus.handle(cmd)


def remove_module(
    fqn: Annotated[str, Argument(help="Module FQN to remove (要移除的模块 FQN)")],
) -> None:
    cmd = RemoveModuleCommand(fqn=ModuleFqn(fqn))
    _remove_module(cmd)
