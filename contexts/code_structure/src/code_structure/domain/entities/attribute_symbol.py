from code_structure.domain.identities.symbol_ids import AttributeId
from foundation.building_blocks.entity import Entity
from foundation.common_types.fqns.fqn import AttributeFqn


class AttributeSymbol(Entity):
    id: AttributeId
    fqn: AttributeFqn
    name: str
