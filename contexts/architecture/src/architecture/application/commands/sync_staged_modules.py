import logging
from dataclasses import dataclass
from pathlib import Path
from architecture.application.ports.code_scanner import CodeScanner
from architecture.application.ports.unit_of_work import UnitOfWork
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
        module_fqns = FqnService.collect_fqns(parsed_modules)
        modules = uow.repository.find_by_fqns(module_fqns)
        module_registry = ModuleRegistry.init(modules)
        sync_modules_service = SyncModuleService(module_registry)
        sync_modules = sync_modules_service.sync_from_parsed_modules(parsed_modules)
        
        uow.repository.save_all(sync_modules)
        
        for deleted_module in module_registry.deleted_modules:
            uow.repository.delete(deleted_module)