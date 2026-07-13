from dataclasses import dataclass, field
from architecture.domain.aggregates.file_module import FileModule
from foundation.common_types.identities.module_id import ModuleId
from foundation.common_types.fqns.fqn import ModuleFqn


@dataclass
class FileModuleRegistry:
    _store_by_fqn: dict[ModuleFqn, FileModule] = field(init=False)
    _store_by_id: dict[ModuleId, FileModule] = field(init=False)
    _fqn_id_map: dict[ModuleFqn, ModuleId] = field(init=False)
    dirty_modules: set[FileModule] = field(init=False)
    deleted_modules: set[FileModule] = field(init=False)

    def __post_init__(self):
        self._store_by_fqn = {}
        self._store_by_id = {}
        self._fqn_id_map = {}
        self.dirty_modules = set()
        self.deleted_modules = set()

    @classmethod
    def init(cls, modules: list[FileModule] | None = None) -> "FileModuleRegistry":
        registry = cls()
        if modules is not None:
            for module in modules:
                registry._store_by_fqn[module.fqn] = module
                registry._store_by_id[module.id] = module
                registry._fqn_id_map[module.fqn] = module.id
        return registry

    def register(self, module: FileModule):
        self._store_by_fqn[module.fqn] = module
        self._store_by_id[module.id] = module
        self._fqn_id_map[module.fqn] = module.id
        self.dirty_modules.add(module)

    def has_fqn(self, fqn: ModuleFqn) -> bool:
        return fqn in self._store_by_fqn

    def get_by_fqn(self, fqn: ModuleFqn) -> FileModule:
        module = self._store_by_fqn.get(fqn)
        if module is None:
            raise ValueError(f"FileModule with FQN {fqn} not found")
        return module

    def find_by_fqn(self, fqn: ModuleFqn) -> FileModule | None:
        return self._store_by_fqn.get(fqn)

    def get_id_by_fqn(self, fqn: ModuleFqn) -> ModuleId:
        return self._fqn_id_map[fqn]

    def mark_dirty(self, module: FileModule):
        self.dirty_modules.add(module)

    def _delete(self, module: FileModule):
        module.mark_as_deleted()
        self.deleted_modules.add(module)

    def delete_by_fqn(self, fqn: ModuleFqn):
        if fqn not in self._store_by_fqn:
            return
        module = self._store_by_fqn[fqn]
        self._delete(module)

    def ensure_file_module(self, fqn: ModuleFqn) -> FileModule:
        """确保 file module 存在，已存在则直接返回"""
        if fqn in self._store_by_fqn:
            return self._store_by_fqn[fqn]
        module = FileModule.create(fqn=fqn, name=fqn.symbol)
        self.register(module)
        return module
