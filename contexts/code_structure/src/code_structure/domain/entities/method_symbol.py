from types import MethodDescriptorType
from code_structure.domain.identities.symbol_ids import MethodId
from code_structure.domain.value_objects.location import Location
from foundation.building_blocks.entity import Entity


class MethodSymbol(Entity):
    id: MethodId
    fqn: MethodDescriptorType
    name: str
    location: Location