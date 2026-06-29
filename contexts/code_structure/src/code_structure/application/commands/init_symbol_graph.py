from dataclasses import dataclass
from code_structure.application.ports.symbol_graph_admin import SymbolGraphAdmin
from code_structure.application.ports.unit_of_work import UnitOfWork
from foundation.building_blocks.command import Command


class InitSymbolGraphCommand(Command):
    ...


@dataclass
class InitSymbolGraphCommandHandler:
    symbol_graph_admin: SymbolGraphAdmin

    def execute(self, cmd: InitSymbolGraphCommand, uow: UnitOfWork) -> None:
        self.symbol_graph_admin.purge_data()
        file_modules = uow.file_modules.get_all_modules()
        print(len(file_modules))
        