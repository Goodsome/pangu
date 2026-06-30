from dataclasses import dataclass, field

from code_structure.domain.aggregates.variable_symbol import VariableSymbol
from code_structure.domain.identities.symbol_ids import VariableId
from foundation.common_types.fqns.fqn import VariableFqn


@dataclass
class VariableRegistry:

    _store_by_fqn: dict[VariableFqn, VariableSymbol] = field(init=False)
    _store_by_id: dict[VariableId, VariableSymbol] = field(init=False)
    _fqn_id_map: dict[VariableFqn, VariableId] = field(init=False)
    dirty_variables: set[VariableSymbol] = field(init=False)

    def __post_init__(self):
        self._store_by_fqn = {}
        self._store_by_id = {}
        self._fqn_id_map = {}
        self.dirty_variables = set()

    @classmethod
    def init(cls, variables: list[VariableSymbol]) -> "VariableRegistry":
        registry = cls()
        for v in variables:
            registry._store_by_fqn[v.fqn] = v
            registry._store_by_id[v.id] = v
            registry._fqn_id_map[v.fqn] = v.id
        return registry

    def register(self, var: VariableSymbol):
        self._store_by_fqn[var.fqn] = var
        self._store_by_id[var.id] = var
        self._fqn_id_map[var.fqn] = var.id
        self.dirty_variables.add(var)
