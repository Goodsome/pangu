from dataclasses import dataclass, field

from code_structure.domain.aggregates.class_symbol import ClassSymbol
from code_structure.domain.identities.symbol_ids import ClassId
from foundation.common_types.fqns.fqn import ClassFqn, SymbolFqn


@dataclass
class ClassRegistry:
    _store_by_fqn: dict[ClassFqn, ClassSymbol] = field(init=False)
    _store_by_id: dict[ClassId, ClassSymbol] = field(init=False)
    _fqn_id_map: dict[ClassFqn, ClassId] = field(init=False)
    dirty_classes: set[ClassSymbol] = field(init=False)

    def __post_init__(self):
        self._store_by_fqn = {}
        self._store_by_id = {}
        self._fqn_id_map = {}
        self.dirty_classes = set()

    @classmethod
    def init(cls, classes: list[ClassSymbol]) -> ClassRegistry:
        registry = cls()
        for c in classes:
            registry._store_by_fqn[c.fqn] = c
            registry._store_by_id[c.id] = c
            registry._fqn_id_map[c.fqn] = c.id
        return registry

    def register(self, cls: ClassSymbol):
        self._store_by_fqn[cls.fqn] = cls
        self._store_by_id[cls.id] = cls
        self._fqn_id_map[cls.fqn] = cls.id
        self.dirty_classes.add(cls)

    def contains_fqn(self, fqn: SymbolFqn) -> bool:
        return fqn in self._store_by_fqn
