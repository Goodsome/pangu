from dataclasses import dataclass
from architecture.application.ports.code_scanner import CodeScanner
from architecture.application.ports.graph_admin import GraphAdmin
from architecture.application.ports.unit_of_work import UnitOfWork
from architecture.domain.aggregates.base_module import BaseModule
from architecture.domain.aggregates.file_module import FileModule
from architecture.domain.aggregates.package_module import PackageModule
from architecture.domain.services.context_registry import ContextRegistry
from architecture.domain.services.graph_builder import GraphBuilder
from foundation.common_types.fqns.fqn import ModuleFqn
from architecture.domain.value_objects.parsed_module import ParsedModule
from foundation.common_types.context_name import ContextName
from foundation.building_blocks.command import Command


class InitProjectGraphCommand(Command): ...


@dataclass
class InitProjectGraphHandler:
    graph_admin: GraphAdmin
    code_scanner: CodeScanner

    def execute(self, cmd: InitProjectGraphCommand, uow: UnitOfWork):
        self.graph_admin.purge_data()
        parsed_modules: list[ParsedModule] = []
        for context_name in ContextName:
            root_path = ContextRegistry.get_context_root_path(context_name)
            parsed_modules.extend(self.code_scanner.scan_directory(root_path=root_path))
        module_registry: dict[ModuleFqn, BaseModule] = {}
        graph_builder = GraphBuilder(module_registry=module_registry)
        graph_builder.build_from_parsed_modules(parsed_modules)
        modules = list(module_registry.values())
        file_modules = [m for m in modules if isinstance(m, FileModule)]
        package_modules = [m for m in modules if isinstance(m, PackageModule)]
        uow.file_modules.add_all(file_modules)
        uow.packages.add_all(package_modules)
