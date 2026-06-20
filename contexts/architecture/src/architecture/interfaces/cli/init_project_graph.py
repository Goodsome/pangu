from pathlib import Path
from typing import Annotated
from dependency_injector.wiring import Provide, inject
from typer import Argument
from architecture.application.commands.init_project_graph import InitProjectGraphCommand
from architecture.infrastructure.message_bus import MessageBus

@inject
def _init_project_graph(
    cmd: InitProjectGraphCommand,
    message_bus: MessageBus = Provide["architecture_container.message_bus"],
):
    message_bus.handle(cmd)

def init_project_graph() -> None:
    cmd = InitProjectGraphCommand(
    )
    _init_project_graph(cmd)
