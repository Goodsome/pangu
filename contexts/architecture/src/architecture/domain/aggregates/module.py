from architecture.domain.events.module_added_dependency import ModuleAddedDependency
from architecture.domain.events.module_removed_dependency import ModuleRemovedDependency
from architecture.domain.identities.module_id import ModuleId
from architecture.domain.mutasions.add_depends_on_edge import AddDependsEdgeMutation
from architecture.domain.mutasions.remove_depends_on_edge import RemoveDependsEdgeMutation
from architecture.domain.value_objects.fqn import ModuleFqn
from pydantic import PrivateAttr

from codegen.shared.domain.core.aggregate_root import AggregateRoot


class Module(AggregateRoot[ModuleId]):
    fqn: ModuleFqn
    name: str
    is_package: bool

    _dependencies: set[ModuleId] = PrivateAttr(default_factory=set)

    @classmethod
    def reconstitute(
        cls,
        module_id: str,
        fqn: str,
        name: str,
        is_package: bool,
        dependencies: set[str],
    ) -> "Module":
        instance = cls(
            id=ModuleId.reconstitute(module_id),
            fqn=ModuleFqn(fqn),
            name=name,
            is_package=is_package,
        )

        _dependencies = {ModuleId.reconstitute(i) for i in dependencies}
        instance._dependencies = _dependencies

        return instance

    def add_dependency(self, target_module_id: ModuleId) -> None:
        if target_module_id == self.id:
            raise ValueError("module can not dep self")
        if target_module_id in self._dependencies:
            return
        self._dependencies.add(target_module_id)
        event = ModuleAddedDependency(
            module_id=self.id, target_module_id=target_module_id
        )
        self.add_domain_event(event)
        mutation = AddDependsEdgeMutation(
            source=self.id,
            target=target_module_id
        )
        self.add_mutation(mutation)

    def remove_dependency(self, target_module_id: ModuleId) -> None:
        if target_module_id not in self._dependencies:
            return
        self._dependencies.remove(target_module_id)
        event = ModuleRemovedDependency(
            module_id=self.id, target_module_id=target_module_id
        )
        self.add_domain_event(event)
        mutation = RemoveDependsEdgeMutation(
            source=self.id,
            target=target_module_id
        )
        self.add_mutation(mutation)
