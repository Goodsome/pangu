from abc import ABC, abstractmethod
from architecture.domain.aggregates.module import Module
from architecture.domain.identities.module_id import ModuleId
from architecture.domain.value_objects.fqn import ModuleFqn
from codegen.shared.domain.ports.repository import Repository



class ModuleRepository(Repository[Module, ModuleId], ABC):

    @abstractmethod
    def find_by_fqn(self, fqn: ModuleFqn) -> Module | None: ...

    @abstractmethod
    def delete_all(self, ids: list[ModuleId]) -> None: ...

    @abstractmethod
    def update_fqn_prefix(self, old_fqn: ModuleFqn, new_fqn: ModuleFqn) -> None: ...

    @abstractmethod
    def get_dependencies(self, id: ModuleId) -> list[ModuleFqn]: ...