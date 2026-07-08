from foundation.building_blocks.value_object import ValueObject
from foundation.common_types.fqns.fqn import SymbolFqn


class ParsedReference(ValueObject):
    target_fqn: SymbolFqn
    alias: str | None = None
