from code_structure.domain.identities.symbol_ids import MethodId
from foundation.building_blocks.entity import Entity
from foundation.common_types.fqns.fqn import MethodFqn


class MethodSymbol(Entity):
    id: MethodId
    fqn: MethodFqn
    name: str