from abc import ABC, abstractmethod
from code_structure.domain.aggregates.file_module import FileModule
from foundation.common_types.fqns.fqn import ModuleFqn
from code_structure.domain.value_objects.parsed_import import ParsedImport
from foundation.common_types.identities.module_id import ModuleId
from foundation.persistence.ports.repository import Repository


class FileModuleRepository(Repository[FileModule, ModuleId], ABC):
    @abstractmethod
    def get_all_modules(self) -> list[FileModule]: ...

    @abstractmethod
    def get_by_fqn(self, fqn: ModuleFqn) -> FileModule: ...

    @abstractmethod
    def get_external_dependencies(self, fqn: ModuleFqn) -> list[ParsedImport]: ...
