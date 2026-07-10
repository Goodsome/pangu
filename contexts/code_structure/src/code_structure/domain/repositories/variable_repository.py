from abc import ABC, abstractmethod
from code_structure.domain.aggregates.variable_symbol import VariableSymbol
from code_structure.domain.identities.symbol_ids import VariableId
from foundation.persistence.ports.repository import Repository


class VariableRepository(Repository[VariableSymbol, VariableId], ABC):
    @abstractmethod
    def find_by_fqn_prefix(self, prefix: str) -> list[VariableSymbol]:
        """Find VariableSymbols by FQN prefix"""
        ...

