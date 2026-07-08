from abc import ABC, abstractmethod

from code_structure.domain.aggregates.class_symbol import ClassSymbol
from code_structure.domain.identities.symbol_ids import ClassId
from foundation.common_types.fqns.fqn import ClassFqn
from foundation.persistence.ports.repository import Repository


class ClassRepository(Repository[ClassSymbol, ClassId], ABC):
    @abstractmethod
    def get_by_fqn(self, fqn: ClassFqn) -> ClassSymbol:
        """Get ClassSymbol by its FQN"""
        ...
