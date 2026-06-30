from dataclasses import dataclass, field

from code_structure.domain.aggregates.function_symbol import FunctionSymbol
from code_structure.domain.identities.symbol_ids import FunctionId
from foundation.common_types.fqns.fqn import FunctionFqn


@dataclass
class FunctionRegistry:

    _store_by_fqn: dict[FunctionFqn, FunctionSymbol] = field(init=False)
    _store_by_id: dict[FunctionId, FunctionSymbol] = field(init=False)
    _fqn_id_map: dict[FunctionFqn, FunctionId] = field(init=False)
    dirty_functions: set[FunctionSymbol] = field(init=False)

    def __post_init__(self):
        self._store_by_fqn = {}
        self._store_by_id = {}
        self._fqn_id_map = {}
        self.dirty_functions = set()

    @classmethod
    def init(cls, functions: list[FunctionSymbol]) -> "FunctionRegistry":
        registry = cls()
        for f in functions:
            registry._store_by_fqn[f.fqn] = f
            registry._store_by_id[f.id] = f
            registry._fqn_id_map[f.fqn] = f.id
        return registry

    def register(self, func: FunctionSymbol):
        self._store_by_fqn[func.fqn] = func
        self._store_by_id[func.id] = func
        self._fqn_id_map[func.fqn] = func.id
        self.dirty_functions.add(func)
