from abc import ABC, abstractmethod
from collections.abc import Collection
from architecture.domain.aggregates.package_module import PackageModule
from foundation.common_types.identities.module_id import ModuleId
from foundation.common_types.fqns.fqn import ModuleFqn
from foundation.persistence.ports.repository import Repository


class PackageModuleRepository(Repository[PackageModule, ModuleId], ABC):
    @abstractmethod
    def find_by_fqn(self, fqn: ModuleFqn) -> PackageModule | None: ...

    @abstractmethod
    def find_by_fqns(self, fqns: Collection[ModuleFqn]) -> list[PackageModule]: ...

    @abstractmethod
    def delete_all(self, ids: list[ModuleId]) -> None: ...

    @abstractmethod
    def update_fqn_prefix(self, old_fqn: ModuleFqn, new_fqn: ModuleFqn) -> None: ...

    @abstractmethod
    def find_containing(self, child_fqn: ModuleFqn) -> PackageModule | None: ...
