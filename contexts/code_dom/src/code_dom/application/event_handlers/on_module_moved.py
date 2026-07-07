import logging
from dataclasses import dataclass
from code_dom.application.ports.unit_of_work import UnitOfWork
from foundation.integration_events.module_moved import ModuleMovedIntegrationEvent
from foundation.system.file_system_port import FileSystemPort

logger = logging.getLogger(__name__)


@dataclass
class OnModuleMoved:
    file_system: FileSystemPort

    def execute_physical_move(
        self, event: ModuleMovedIntegrationEvent, uow: UnitOfWork
    ):
        self.file_system.move(event.old_path, event.new_path)
        for caller_path in event.affected_callers:
            caller = uow.documents.get(caller_path)
            caller.update_imports(event.old_module_fqn, event.new_module_fqn)
            uow.documents.save(caller)
