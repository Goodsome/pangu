from typing import override
from architecture.domain.aggregates.base_module import BaseModule
from architecture.domain.events.module_added_contains import ModuleAddedContains
from architecture.domain.events.module_added_dependency import ModuleAddedDependency
from architecture.domain.events.module_removed_contains import ModuleRemovedContains
from architecture.domain.events.package_module_created import PackageModuleCreated
from architecture.domain.events.package_module_deleted import PackageModuleDeleted
from architecture.domain.events.package_module_moved import PackageModuleMoved
from foundation.common_types.identities.module_id import ModuleId
from pydantic import PrivateAttr
from foundation.common_types.fqns.fqn import ModuleFqn


class PackageModule(BaseModule):
    fqn: ModuleFqn
    _contains: set[ModuleId] = PrivateAttr(default_factory=set)

    @property
    def contains(self) -> frozenset[ModuleId]:
        return frozenset(self._contains)

    @classmethod
    def create(cls, fqn: ModuleFqn, name: str) -> "PackageModule":
        module = cls(id=ModuleId.create(), fqn=fqn, name=name)
        event = PackageModuleCreated(module_id=module.id, module_fqn=fqn)
        module.add_domain_event(event)
        return module

    @classmethod
    def reconstitute(
        cls,
        module_id: str,
        fqn: str,
        name: str,
        dependencies: set[str],
        contains: set[str],
    ) -> "PackageModule":
        instance = cls(
            id=ModuleId.reconstitute(module_id),
            fqn=ModuleFqn(fqn),
            name=name,
        )
        instance._dependencies = {ModuleId.reconstitute(i) for i in dependencies}
        instance._contains = {ModuleId.reconstitute(i) for i in contains}
        return instance

    def mark_as_deleted(self) -> None:
        event = PackageModuleDeleted(module_id=self.id, module_fqn=self.fqn)
        self.add_domain_event(event)

    def moved(self, new_fqn: ModuleFqn) -> None:
        old_fqn = self.fqn
        self.fqn = new_fqn
        event = PackageModuleMoved(module_id=self.id, old_fqn=old_fqn, new_fqn=new_fqn)
        self.add_domain_event(event)

    @override
    def add_dependency(self, target_module_id: ModuleId) -> None:
        if target_module_id == self.id:
            raise ValueError("module can not dep self")
        if target_module_id in self.dependencies:
            return
        if target_module_id not in self.contains:
            raise ValueError("package can not depend on module not contained")
        self._dependencies.add(target_module_id)
        event = ModuleAddedDependency(
            module_id=self.id, target_module_id=target_module_id
        )
        self.add_domain_event(event)

    def add_contains(self, child_module_id: ModuleId) -> None:
        if child_module_id == self.id:
            raise ValueError("module can not contain self")
        if child_module_id in self.contains:
            return
        self._contains.add(child_module_id)
        event = ModuleAddedContains(module_id=self.id, child_module_id=child_module_id)
        self.add_domain_event(event)

    def remove_contains(self, child_module_id: ModuleId) -> None:
        if child_module_id not in self.contains:
            return
        if child_module_id in self.dependencies:
            raise ValueError("module can not remove module that is a dependency")
        self._contains.remove(child_module_id)
        event = ModuleRemovedContains(
            module_id=self.id, child_module_id=child_module_id
        )
        self.add_domain_event(event)
