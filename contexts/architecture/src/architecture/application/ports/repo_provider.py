from abc import ABC, abstractmethod
from architecture.domain.aggregates.file_module import FileModule
from architecture.domain.aggregates.package_module import PackageModule
from architecture.domain.repositories.file_module_repository import FileModuleRepository
from architecture.domain.repositories.package_module_repository import (
    PackageModuleRepository,
)
from foundation.common_types.fqns.fqn import ModuleFqn
from foundation.persistence.ports.outbox_repository import OutboxRepository


class RepoProvider(ABC):
    @property
    @abstractmethod
    def file_modules(self) -> FileModuleRepository: ...

    @property
    @abstractmethod
    def packages(self) -> PackageModuleRepository: ...

    @property
    @abstractmethod
    def outbox(self) -> OutboxRepository: ...

    def find_module_by_fqn(self, fqn: ModuleFqn) -> FileModule | PackageModule | None:
        return self.file_modules.find_by_fqn(fqn) or self.packages.find_by_fqn(fqn)
