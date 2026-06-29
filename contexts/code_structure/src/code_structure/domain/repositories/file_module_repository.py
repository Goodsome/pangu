from abc import ABC, abstractmethod
from code_structure.domain.aggregates.file_module import FileModule
from foundation.common_types.identities.module_id import ModuleId
from foundation.persistence.ports.repository import Repository


class FileModuleRepository(Repository[FileModule, ModuleId], ABC):

    @abstractmethod
    def get_all_modules(self) -> list[FileModule]: ...
