import logging
from dataclasses import dataclass
from code_dom.application.ports.repo_provider import RepoProvider
from foundation.integration_events.module_deleted import ModuleDeletedIntegrationEvent
from foundation.system.file_system_port import FileSystemPort

logger = logging.getLogger(__name__)


@dataclass
class OnModuleDeleted:
    file_system: FileSystemPort

    def clean_filesystem(self, event: ModuleDeletedIntegrationEvent, uow: RepoProvider):
        if event.is_package:
            self.file_system.delete_directory(event.module_path)
        else:
            self.file_system.delete_file(event.module_path)
