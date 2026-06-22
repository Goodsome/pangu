from dependency_injector.wiring import Provide, inject
from architecture.application.commands.init_project_graph import InitProjectGraphCommand
from foundation.message_bus.message_bus import BaseMessageBus


@inject
def _init_project_graph(
    cmd: InitProjectGraphCommand,
    message_bus: BaseMessageBus = Provide["architecture_container.message_bus"],
):
    message_bus.handle(cmd)


def init_project_graph() -> None:
    cmd = InitProjectGraphCommand()
    _init_project_graph(cmd)
