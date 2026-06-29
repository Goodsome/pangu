from abc import ABC
from code_structure.domain.aggregates.function_symbol import FunctionSymbol
from code_structure.domain.identities.symbol_ids import FunctionId
from foundation.persistence.ports.repository import Repository


class FunctionRepository(Repository[FunctionSymbol, FunctionId], ABC):
    ...