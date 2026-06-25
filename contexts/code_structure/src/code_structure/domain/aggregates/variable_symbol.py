from code_structure.domain.identities.symbol_ids import VariableId
from code_structure.domain.value_objects.location import Location
from foundation.building_blocks.aggregate_root import AggregateRoot
from foundation.common_types.fqns.fqn import VariableFqn


class VariableSymbol(AggregateRoot[VariableId]):
    name: str
    fqn: VariableFqn
    location: Location