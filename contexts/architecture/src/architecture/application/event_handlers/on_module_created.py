from dataclasses import dataclass

from architecture.domain.events.module_created import ModuleCreated
from architecture.domain.services.fqn_service import FqnService
from architecture.domain.value_objects.fqn import ModuleFqn
from architecture.infrastructure.unit_of_work import UnitOfWork

from codegen.shared.application.integration_events.module_created import (
    ModuleCreatedIntegrationEvent,
)
from codegen.shared.domain.ports.file_system_port import FileSystemPort


@dataclass
class OnModuleCreated:
    file_system: FileSystemPort

    def to_integration(self, event: ModuleCreated, uow: UnitOfWork):
        ie = ModuleCreatedIntegrationEvent(
            module_fqn=event.module_fqn, is_package=event.is_package
        )
        uow.save_outbox_message(ie)
        yield from []

    def create_file(self, event: ModuleCreatedIntegrationEvent, uow: UnitOfWork):
        module_fqn = ModuleFqn(event.module_fqn)
        file_path = FqnService.build_path(module_fqn, event.is_package)
        
        self.file_system.write_file(file_path, content="")
        yield from []
