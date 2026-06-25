from typing import Annotated
from dependency_injector.wiring import Provide, inject
from typer import Argument
from architecture.application.commands.create_package import CreatePackageCommand
from foundation.common_types.fqns.fqn import ModuleFqn
from architecture.infrastructure.message_bus import MessageBus


@inject
def _create_package(
    cmd: CreatePackageCommand,
    message_bus: MessageBus = Provide["architecture_container.message_bus"],
):
    message_bus.handle(cmd)


def create_package(
    fqn: Annotated[str, Argument(help="Package FQN to create (要创建的包 FQN)")],
) -> None:
    cmd = CreatePackageCommand(fqn=ModuleFqn(fqn))
    _create_package(cmd)
