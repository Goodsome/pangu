from code_structure.domain.identities.symbol_ids import FunctionId
from code_structure.domain.value_objects.location import Location
from foundation.building_blocks.aggregate_root import AggregateRoot
from foundation.common_types.fqns.fqn import FunctionFqn


class FunctionSymbol(AggregateRoot[FunctionId]):
    name: str
    fqn: FunctionFqn
    location: Location