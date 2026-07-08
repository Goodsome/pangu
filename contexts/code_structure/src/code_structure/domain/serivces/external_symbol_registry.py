from dataclasses import dataclass, field
from code_structure.domain.aggregates.external_symbol import ExternalSymbol
from code_structure.domain.identities.symbol_ids import ExternalSymbolId
from foundation.common_types.fqns.fqn import SymbolFqn


@dataclass
class ExternalSymbolRegistry:
    _store_by_fqn: dict[SymbolFqn, ExternalSymbol] = field(init=False)
    _store_by_id: dict[ExternalSymbolId, ExternalSymbol] = field(init=False)
    _fqn_id_map: dict[SymbolFqn, ExternalSymbolId] = field(init=False)
    dirty_external_symbols: set[ExternalSymbol] = field(init=False)

    def __post_init__(self):
        self._store_by_fqn = {}
        self._store_by_id = {}
        self._fqn_id_map = {}
        self.dirty_external_symbols = set()

    @classmethod
    def init(cls, external_symbols: list[ExternalSymbol]) -> "ExternalSymbolRegistry":
        registry = cls()
        for s in external_symbols:
            registry._store_by_fqn[s.fqn] = s
            registry._store_by_id[s.id] = s
            registry._fqn_id_map[s.fqn] = s.id
        return registry

    def register(self, symbol: ExternalSymbol):
        self._store_by_fqn[symbol.fqn] = symbol
        self._store_by_id[symbol.id] = symbol
        self._fqn_id_map[symbol.fqn] = symbol.id
        self.dirty_external_symbols.add(symbol)

    def get_by_fqn(self, fqn: SymbolFqn) -> ExternalSymbol | None:
        return self._store_by_fqn.get(fqn)

    def contains_fqn(self, fqn: SymbolFqn) -> bool:
        return fqn in self._store_by_fqn
