from dataclasses import dataclass
from pathlib import Path

from architecture.domain.events.module_deleted import ModuleDeleted
from architecture.domain.services.fqn_service import FqnService
from architecture.domain.value_objects.fqn import ModuleFqn
from architecture.infrastructure.unit_of_work import UnitOfWork

from codegen.shared.application.integration_events.module_deleted import (
    ModuleDeletedIntegrationEvent,
)
from codegen.shared.domain.ports.file_system_port import FileSystemPort


@dataclass
class OnModuleDeleted:
    file_system: FileSystemPort

    def to_integration(self, event: ModuleDeleted, uow: UnitOfWork):
        ie = ModuleDeletedIntegrationEvent(
            module_fqn=str(event.module_fqn),
            is_package=event.is_package,
        )
        uow.save_outbox_message(ie)
        yield from []

    def clean_filesystem(self, event: ModuleDeletedIntegrationEvent, uow: UnitOfWork):
        fqn = ModuleFqn(event.module_fqn)
        module_path = FqnService.build_path(fqn)
        if event.is_package:
            self.file_system.delete_directory(module_path)
        else:
            file_path = module_path.with_suffix(".py")
            self.file_system.delete_file(file_path)
            
        yield from []
        