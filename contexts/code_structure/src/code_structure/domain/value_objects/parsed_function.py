from foundation.building_blocks.value_object import ValueObject
from foundation.common_types.fqns.fqn import SymbolFqn


class ParsedFunction(ValueObject):
    name: str
    references: list[SymbolFqn]
