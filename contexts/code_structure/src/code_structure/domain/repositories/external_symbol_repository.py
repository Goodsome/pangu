from abc import ABC, abstractmethod
from code_structure.domain.aggregates.external_symbol import ExternalSymbol
from code_structure.domain.identities.symbol_ids import ExternalSymbolId
from foundation.common_types.fqns.fqn import SymbolFqn
from foundation.persistence.ports.repository import Repository


class ExternalSymbolRepository(Repository[ExternalSymbol, ExternalSymbolId], ABC):
    @abstractmethod
    def get_by_fqn(self, fqn: SymbolFqn) -> ExternalSymbol:
        """Get ExternalSymbol by its FQN"""
        ...
