from foundation.building_blocks.aggregate_root import AggregateRoot
from foundation.common_types.fqns.fqn import SymbolFqn
from code_structure.domain.identities.symbol_ids import ExternalSymbolId


class ExternalSymbol(AggregateRoot[ExternalSymbolId]):
    name: str
    fqn: SymbolFqn
