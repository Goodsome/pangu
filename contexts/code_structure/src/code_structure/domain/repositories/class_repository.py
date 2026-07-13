from abc import ABC, abstractmethod

from code_structure.domain.aggregates.class_symbol import ClassSymbol
from code_structure.domain.identities.symbol_ids import ClassId
from foundation.common_types.fqns.fqn import ClassFqn, ModuleFqn
from foundation.persistence.ports.repository import Repository


class ClassRepository(Repository[ClassSymbol, ClassId], ABC):
    @abstractmethod
    def get_by_fqn(self, fqn: ClassFqn) -> ClassSymbol:
        """Get ClassSymbol by its FQN"""
        ...

    @abstractmethod
    def find_affected_callers(self, class_id: ClassId) -> list[ModuleFqn]:
        """Find all ModuleFqns of files that contain symbols referencing the class"""
        ...

    @abstractmethod
    def find_by_fqn_prefix(self, prefix: str) -> list[ClassSymbol]:
        """Find ClassSymbols by FQN prefix"""
        ...
