import logging
from dataclasses import dataclass
from pathlib import Path
from architecture.application.ports.code_scanner import CodeScanner
from architecture.application.ports.unit_of_work import UnitOfWork
from architecture.domain.services.file_module_registry import FileModuleRegistry
from architecture.domain.services.fqn_service import FqnService
from architecture.domain.services.package_module_registry import PackageModuleRegistry
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

        file_registry = FileModuleRegistry.init(file_modules)
        package_registry = PackageModuleRegistry.init(package_modules)
        sync_service = SyncModuleService(file_registry, package_registry)
        sync_service.sync_from_parsed_modules(parsed_modules)

        uow.file_modules.save_all(list(file_registry.dirty_modules))
        uow.packages.save_all(list(package_registry.dirty_modules))

        for deleted in file_registry.deleted_modules:
            uow.file_modules.delete(deleted)
        for deleted in package_registry.deleted_modules:
            uow.packages.delete(deleted)
