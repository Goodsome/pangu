from dataclasses import dataclass, field
from architecture.domain.aggregates.module import Module
from foundation.common_types.identities.module_id import ModuleId
from foundation.common_types.fqns.fqn import ModuleFqn


@dataclass
class ModuleRegistry:
    _store_by_fqn: dict[ModuleFqn, Module] = field(init=False)
    _store_by_id: dict[ModuleId, Module] = field(init=False)
    _fqn_id_map: dict[ModuleFqn, ModuleId] = field(init=False)
    dirty_modules: set[Module] = field(init=False)
    deleted_modules: set[Module] = field(init=False)

    def __post_init__(self):
        self._store_by_fqn = {}
        self._store_by_id = {}
        self._fqn_id_map = {}
        self.dirty_modules = set()
        self.deleted_modules = set()

    @classmethod
    def init(cls, modules: list[Module]) -> ModuleRegistry:
        registry = cls()
        for module in modules:
            registry._store_by_fqn[module.fqn] = module
            registry._store_by_id[module.id] = module
            registry._fqn_id_map[module.fqn] = module.id
        return registry

    def register(self, module: Module):
        self._store_by_fqn[module.fqn] = module
        self._store_by_id[module.id] = module
        self._fqn_id_map[module.fqn] = module.id
        self.dirty_modules.add(module)

    def has_fqn(self, fqn: ModuleFqn) -> bool:
        return fqn in self._store_by_fqn

    def get_by_fqn(self, fqn: ModuleFqn) -> Module:
        module = self._store_by_fqn.get(fqn)
        if module is None:
            raise ValueError(f"Module with FQN {fqn} not found")
        return module

    def find_module_by_fqn(self, fqn: ModuleFqn) -> Module | None:
        return self._store_by_fqn.get(fqn)

    def get_id_by_fqn(self, fqn: ModuleFqn) -> ModuleId:
        return self._fqn_id_map[fqn]

    def ensure_module(self, fqn: ModuleFqn, is_package: bool) -> Module:
        if fqn in self._store_by_fqn:
            return self._store_by_fqn[fqn]
        module = Module.create(fqn=fqn, name=fqn.symbol, is_package=is_package)
        self.register(module)
        if fqn.is_root:
            return module
        parent_module = self.ensure_module(fqn=fqn.parent_fqn, is_package=True)
        parent_module.add_contains(module.id)
        self.mark_dirty(parent_module)
        return module

    def mark_dirty(self, module: Module):
        self.dirty_modules.add(module)

    def _delete(self, module: Module):
        module.mark_as_deleted()
        self.deleted_modules.add(module)

    def delete_by_fqn(self, fqn: ModuleFqn):
        if fqn not in self._store_by_fqn:
            return
        module = self._store_by_fqn[fqn]
        self._delete(module)
