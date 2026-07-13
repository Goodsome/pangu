from dataclasses import dataclass
from architecture.application.ports.code_scanner import CodeScanner
from architecture.application.ports.graph_admin import GraphAdmin
from architecture.application.ports.unit_of_work import UnitOfWork
from architecture.domain.services.context_registry import ContextRegistry
from architecture.domain.services.file_module_registry import FileModuleRegistry
from architecture.domain.services.package_module_registry import PackageModuleRegistry
from architecture.domain.services.sync_module_service import SyncModuleService
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
        file_registry = FileModuleRegistry.init()
        package_registry = PackageModuleRegistry.init()
        sync_service = SyncModuleService(file_registry, package_registry)
        sync_service.sync_from_parsed_modules(parsed_modules)

        uow.file_modules.add_all(list(file_registry.dirty_modules))
        uow.packages.add_all(list(package_registry.dirty_modules))
