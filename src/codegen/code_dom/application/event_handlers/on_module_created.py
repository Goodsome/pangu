import logging
from dataclasses import dataclass

from codegen.code_dom.application.ports.unit_of_work import UnitOfWork
from codegen.shared.application.integration_events.module_created import (
    ModuleCreatedIntegrationEvent,
)
from codegen.shared.domain.ports.file_system_port import FileSystemPort

logger = logging.getLogger(__name__)


@dataclass
class OnModuleCreated:
    file_system: FileSystemPort

    def create_file(self, event: ModuleCreatedIntegrationEvent, uow: UnitOfWork):
        self.file_system.write_file(event.module_path, content="")
        yield from []
