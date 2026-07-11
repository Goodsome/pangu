from abc import abstractmethod
from foundation.building_blocks.aggregate_root import AggregateRoot
from architecture.domain.events.module_added_dependency import ModuleAddedDependency
from architecture.domain.events.module_removed_dependency import ModuleRemovedDependency
from foundation.common_types.identities.module_id import ModuleId
from pydantic import PrivateAttr
from foundation.common_types.fqns.fqn import ModuleFqn


class BaseModule(AggregateRoot[ModuleId]):
    fqn: ModuleFqn
    name: str
    _dependencies: set[ModuleId] = PrivateAttr(default_factory=set)

    @property
    def dependencies(self) -> frozenset[ModuleId]:
        return frozenset(self._dependencies)

    @abstractmethod
    def mark_as_deleted(self) -> None: ...

    @abstractmethod
    def moved(self, new_fqn: ModuleFqn) -> None: ...

    def add_dependency(self, target_module_id: ModuleId) -> None:
        if target_module_id == self.id:
            raise ValueError("module can not dep self")
        if target_module_id in self.dependencies:
            return
        self._dependencies.add(target_module_id)
        event = ModuleAddedDependency(
            module_id=self.id, target_module_id=target_module_id
        )
        self.add_domain_event(event)

    def remove_dependency(self, target_module_id: ModuleId) -> None:
        if target_module_id not in self.dependencies:
            return
        self._dependencies.remove(target_module_id)
        event = ModuleRemovedDependency(
            module_id=self.id, target_module_id=target_module_id
        )
        self.add_domain_event(event)

    def sync_dependencies(self, dependencies: set[ModuleId]) -> bool:
        add_dependencies = dependencies - self.dependencies
        remove_dependencies = self.dependencies - dependencies
        if not add_dependencies and (not remove_dependencies):
            return False
        for dependency in add_dependencies:
            self.add_dependency(dependency)
        for dependency in remove_dependencies:
            self.remove_dependency(dependency)
        return True
