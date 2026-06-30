from dataclasses import dataclass, field

from code_structure.domain.aggregates.file_module import FileModule
from foundation.common_types.fqns.fqn import ModuleFqn
from foundation.common_types.identities.module_id import ModuleId


@dataclass
class FileModuleRegistry:

    _store_by_fqn: dict[ModuleFqn, FileModule] = field(init=False)
    _store_by_id: dict[ModuleId, FileModule] = field(init=False)
    dirty_file_modules: set[FileModule] = field(init=False)

    def __post_init__(self):
        self._store_by_fqn = {}
        self._store_by_id = {}
        self.dirty_file_modules = set()
    
    @classmethod
    def init(cls, file_modules: list[FileModule]) -> FileModuleRegistry:
        registry = cls()
        for file_module in file_modules:
            registry._store_by_fqn[file_module.fqn] = file_module
            registry._store_by_id[file_module.id] = file_module
        return registry

    def get_by_fqn(self, fqn: ModuleFqn) -> FileModule:
        module = self._store_by_fqn.get(fqn)
        if module is None:
            raise ValueError(f"Module with FQN {fqn} not found")
        return module
        
    def mark_dirty(self, file_module: FileModule):
        self.dirty_file_modules.add(file_module)