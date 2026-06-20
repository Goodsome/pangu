from dataclasses import dataclass
from pathlib import Path

from architecture.application.ports.code_scanner import CodeScanner
from architecture.application.ports.graph_admin import GraphAdmin
from architecture.domain.services.graph_builder import GraphBuilder
from architecture.infrastructure.unit_of_work import UnitOfWork

from codegen.shared.domain.core.command import Command


class InitProjectGraphCommand(Command): ...


@dataclass
class InitProjectGraphHandler:
    graph_admin: GraphAdmin
    code_scanner: CodeScanner

    def execute(self, cmd: InitProjectGraphCommand, uow: UnitOfWork):
        self.graph_admin.purge_data()
        root_path = Path("contexts/architecture/src")
        parsed_modules = self.code_scanner.scan_directory(
            root_path=root_path,
        )
        graph_builder = GraphBuilder(root_path=root_path)
        modules = graph_builder.build_from_parsed_modules(parsed_modules)

        uow.repository.add_all(modules)
