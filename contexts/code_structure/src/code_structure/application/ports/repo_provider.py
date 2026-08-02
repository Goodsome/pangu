from abc import ABC, abstractmethod
from code_structure.application.ports.symbol_graph_admin import SymbolGraphAdmin
from code_structure.domain.repositories.class_repository import ClassRepository
from code_structure.domain.repositories.external_symbol_repository import (
    ExternalSymbolRepository,
)
from code_structure.domain.repositories.file_module_repository import (
    FileModuleRepository,
)
from code_structure.domain.repositories.function_repository import FunctionRepository
from code_structure.domain.repositories.variable_repository import VariableRepository
from foundation.persistence.ports.outbox_repository import OutboxRepository


class RepoProvider(ABC):
    @property
    @abstractmethod
    def file_modules(self) -> FileModuleRepository: ...

    @property
    @abstractmethod
    def classes(self) -> ClassRepository: ...

    @property
    @abstractmethod
    def functions(self) -> FunctionRepository: ...

    @property
    @abstractmethod
    def variables(self) -> VariableRepository: ...

    @property
    @abstractmethod
    def external_symbols(self) -> ExternalSymbolRepository: ...

    @property
    @abstractmethod
    def graph_admin(self) -> SymbolGraphAdmin: ...

    @property
    @abstractmethod
    def outbox(self) -> OutboxRepository: ...
