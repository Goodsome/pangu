from abc import ABC, abstractmethod
from collections.abc import Iterator
from architecture.domain.aggregates.file_module import FileModule
from architecture.domain.aggregates.package_module import PackageModule
from architecture.domain.repositories.file_module_repository import FileModuleRepository
from architecture.domain.repositories.package_module_repository import (
    PackageModuleRepository,
)
from foundation.building_blocks.event import DomainEvent
from foundation.common_types.fqns.fqn import ModuleFqn
from foundation.persistence.ports.base_unit_of_work import BaseUnitOfWork


class UnitOfWork(BaseUnitOfWork, ABC):
    @property
    @abstractmethod
    def file_modules(self) -> FileModuleRepository: ...

    @property
    @abstractmethod
    def packages(self) -> PackageModuleRepository: ...

    def find_module_by_fqn(self, fqn: ModuleFqn) -> FileModule | PackageModule | None:
        return self.file_modules.find_by_fqn(fqn) or self.packages.find_by_fqn(fqn)

    def collect_events(self) -> Iterator[DomainEvent]:
        yield from self.file_modules.collect_events()
        yield from self.packages.collect_events()
