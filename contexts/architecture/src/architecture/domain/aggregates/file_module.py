from architecture.domain.aggregates.base_module import BaseModule
from architecture.domain.events.file_module_created import FileModuleCreated
from architecture.domain.events.file_module_deleted import FileModuleDeleted
from architecture.domain.events.file_module_moved import FileModuleMoved
from foundation.common_types.identities.module_id import ModuleId
from foundation.common_types.fqns.fqn import ModuleFqn


class FileModule(BaseModule):
    fqn: ModuleFqn

    @classmethod
    def create(cls, fqn: ModuleFqn, name: str) -> "FileModule":
        module = cls(id=ModuleId.create(), fqn=fqn, name=name)
        event = FileModuleCreated(module_id=module.id, module_fqn=fqn)
        module.add_domain_event(event)
        return module

    @classmethod
    def reconstitute(
        cls,
        module_id: str,
        fqn: str,
        name: str,
        dependencies: set[str],
    ) -> "FileModule":
        instance = cls(
            id=ModuleId.reconstitute(module_id),
            fqn=ModuleFqn(fqn),
            name=name,
        )
        instance._dependencies = {ModuleId.reconstitute(i) for i in dependencies}
        return instance

    def mark_as_deleted(self) -> None:
        event = FileModuleDeleted(module_id=self.id, module_fqn=self.fqn)
        self.add_domain_event(event)

    def moved(self, new_fqn: ModuleFqn) -> None:
        old_fqn = self.fqn
        self.fqn = new_fqn
        event = FileModuleMoved(module_id=self.id, old_fqn=old_fqn, new_fqn=new_fqn)
        self.add_domain_event(event)
