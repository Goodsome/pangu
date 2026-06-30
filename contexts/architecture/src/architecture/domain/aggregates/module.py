from foundation.building_blocks.aggregate_root import AggregateRoot
from pydantic import Field
from architecture.domain.events.module_added_contains import ModuleAddedContains
from architecture.domain.events.module_added_dependency import ModuleAddedDependency
from architecture.domain.events.module_created import ModuleCreated
from architecture.domain.events.module_deleted import ModuleDeleted
from architecture.domain.events.module_moved import ModuleMoved
from architecture.domain.events.module_removed_contains import ModuleRemovedContains
from architecture.domain.events.module_removed_dependency import ModuleRemovedDependency
from foundation.common_types.identities.module_id import ModuleId
from architecture.domain.mutations.add_contains_edge import AddContainsEdgeMutation
from architecture.domain.mutations.add_depends_on_edge import AddDependsEdgeMutation
from architecture.domain.mutations.remove_contains_edge import (
    RemoveContainsEdgeMutation,
)
from architecture.domain.mutations.remove_depends_on_edge import (
    RemoveDependsEdgeMutation,
)
from foundation.common_types.fqns.fqn import ModuleFqn


class Module(AggregateRoot[ModuleId]):
    fqn: ModuleFqn
    name: str
    is_package: bool
    dependencies: set[ModuleId] = Field(default_factory=set)
    contains: set[ModuleId] = Field(default_factory=set)

    @classmethod
    def create(cls, fqn: ModuleFqn, name: str, is_package: bool) -> Module:
        module = cls(id=ModuleId.create(), fqn=fqn, name=name, is_package=is_package)
        event = ModuleCreated(
            module_id=module.id, module_fqn=fqn, is_package=is_package
        )
        module.add_domain_event(event)
        return module

    @classmethod
    def reconstitute(
        cls,
        module_id: str,
        fqn: str,
        name: str,
        is_package: bool,
        dependencies: set[str],
        contains: set[str],
    ) -> Module:
        instance = cls(
            id=ModuleId.reconstitute(module_id),
            fqn=ModuleFqn(fqn),
            name=name,
            is_package=is_package,
        )
        _dependencies = {ModuleId.reconstitute(i) for i in dependencies}
        instance.dependencies = _dependencies
        _contains = {ModuleId.reconstitute(i) for i in contains}
        instance.contains = _contains
        return instance

    def mark_as_deleted(self) -> None:
        event = ModuleDeleted(
            module_id=self.id, module_fqn=self.fqn, is_package=self.is_package
        )
        self.add_domain_event(event)

    def moved(self, new_fqn: ModuleFqn) -> None:
        old_fqn = self.fqn
        self.fqn = new_fqn
        event = ModuleMoved(
            module_id=self.id,
            old_fqn=old_fqn,
            new_fqn=new_fqn,
            is_package=self.is_package,
        )
        self.add_domain_event(event)

    def add_dependency(self, target_module_id: ModuleId) -> None:
        if target_module_id == self.id:
            raise ValueError("module can not dep self")
        if target_module_id in self.dependencies:
            return
        if self.is_package and target_module_id not in self.contains:
            raise ValueError("package can not depend on module not contained")
        self.dependencies.add(target_module_id)
        event = ModuleAddedDependency(
            module_id=self.id, target_module_id=target_module_id
        )
        self.add_domain_event(event)
        mutation = AddDependsEdgeMutation(source=self.id, target=target_module_id)
        self.add_mutation(mutation)

    def remove_dependency(self, target_module_id: ModuleId) -> None:
        if target_module_id not in self.dependencies:
            return
        self.dependencies.remove(target_module_id)
        event = ModuleRemovedDependency(
            module_id=self.id, target_module_id=target_module_id
        )
        self.add_domain_event(event)
        mutation = RemoveDependsEdgeMutation(source=self.id, target=target_module_id)
        self.add_mutation(mutation)

    def add_contains(self, child_module_id: ModuleId) -> None:
        if child_module_id == self.id:
            raise ValueError("module can not contain self")
        if child_module_id in self.contains:
            return
        self.contains.add(child_module_id)
        event = ModuleAddedContains(module_id=self.id, child_module_id=child_module_id)
        self.add_domain_event(event)
        mutation = AddContainsEdgeMutation(source=self.id, target=child_module_id)
        self.add_mutation(mutation)

    def remove_contains(self, child_module_id: ModuleId) -> None:
        if child_module_id not in self.contains:
            return
        if child_module_id in self.dependencies:
            raise ValueError("module can not remove module that is a dependency")
        self.contains.remove(child_module_id)
        event = ModuleRemovedContains(
            module_id=self.id, child_module_id=child_module_id
        )
        self.add_domain_event(event)
        mutation = RemoveContainsEdgeMutation(source=self.id, target=child_module_id)
        self.add_mutation(mutation)

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
