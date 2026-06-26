from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import override

from code_structure.domain.repositories.class_repository import ClassRepository
from code_structure.domain.repositories.function_repository import FunctionRepository
from code_structure.domain.repositories.module_repository import ModuleRepository
from code_structure.domain.repositories.variable_repository import VariableRepository
from foundation.building_blocks.event import DomainEvent
from foundation.persistence.base_unit_of_work import BaseUnitOfWork


class UnitOfWork(BaseUnitOfWork, ABC):

    @property
    @abstractmethod
    def modules(self) -> ModuleRepository:
        ...

    @property
    @abstractmethod
    def classes(self) -> ClassRepository:
        ...

    @property
    @abstractmethod
    def functions(self) -> FunctionRepository:
        ...

    @property
    @abstractmethod
    def variables(self) -> VariableRepository:
        ...
        
    @override
    def collect_events(self) -> Iterator[DomainEvent]:
        yield from self.modules.collect_events()
        yield from self.classes.collect_events()
        yield from self.functions.collect_events()
        yield from self.variables.collect_events()
