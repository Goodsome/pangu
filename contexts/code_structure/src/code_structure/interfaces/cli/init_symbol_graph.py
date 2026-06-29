from dependency_injector.wiring import Provide, inject
from code_structure.application.commands.init_symbol_graph import InitSymbolGraphCommand
from foundation.message_bus.message_bus import BaseMessageBus


@inject
def _init_symbol_graph(
    cmd: InitSymbolGraphCommand,
    message_bus: BaseMessageBus = Provide["code_structure_container.message_bus"],
):
    message_bus.handle(cmd)


def init_symbol_graph() -> None:
    cmd = InitSymbolGraphCommand()
    _init_symbol_graph(cmd)
