from abc import ABC, abstractmethod
from collections.abc import Collection
from architecture.domain.aggregates.module import Module
from foundation.common_types.identities.module_id import ModuleId
from foundation.common_types.fqns.fqn import ModuleFqn
from foundation.persistence.ports.repository import Repository


class ModuleRepository(Repository[Module, ModuleId], ABC):
    @abstractmethod
    def find_by_fqn(self, fqn: ModuleFqn) -> Module | None: ...

    @abstractmethod
    def find_by_fqns(self, fqns: Collection[ModuleFqn]) -> list[Module]: ...

    @abstractmethod
    def delete_all(self, ids: list[ModuleId]) -> None: ...

    @abstractmethod
    def update_fqn_prefix(self, old_fqn: ModuleFqn, new_fqn: ModuleFqn) -> None: ...

    @abstractmethod
    def get_dependencies(self, id: ModuleId) -> list[ModuleFqn]: ...
