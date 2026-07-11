import logging
from dataclasses import dataclass
from pathlib import Path
from architecture.application.ports.code_scanner import CodeScanner
from architecture.application.ports.unit_of_work import UnitOfWork
from architecture.domain.aggregates.file_module import FileModule
from architecture.domain.aggregates.package_module import PackageModule
from architecture.domain.services.fqn_service import FqnService
from architecture.domain.services.module_registry import ModuleRegistry
from architecture.domain.services.sync_module_service import SyncModuleService
from foundation.building_blocks.command import Command

logger = logging.getLogger(__name__)


class SyncStagedModulesCommand(Command):
    file_path: list[Path]


@dataclass
class SyncStagedModulesHandler:
    code_scanner: CodeScanner

    def execute(self, cmd: SyncStagedModulesCommand, uow: UnitOfWork) -> None:
        parsed_modules = self.code_scanner.scan_files(cmd.file_path)
        file_fqns, package_fqns = FqnService.collect_fqns_by_type(parsed_modules)
        file_modules = uow.file_modules.find_by_fqns(file_fqns)
        package_modules = uow.packages.find_by_fqns(package_fqns)
        all_modules = list(file_modules) + list(package_modules)
        module_registry = ModuleRegistry.init(all_modules)
        sync_modules_service = SyncModuleService(module_registry)
        sync_modules = sync_modules_service.sync_from_parsed_modules(parsed_modules)

        file_sync = [m for m in sync_modules if isinstance(m, FileModule)]
        package_sync = [m for m in sync_modules if isinstance(m, PackageModule)]
        uow.file_modules.save_all(file_sync)
        uow.packages.save_all(package_sync)

        for deleted_module in module_registry.deleted_modules:
            if isinstance(deleted_module, PackageModule):
                uow.packages.delete(deleted_module)
            else:
                uow.file_modules.delete(deleted_module)
