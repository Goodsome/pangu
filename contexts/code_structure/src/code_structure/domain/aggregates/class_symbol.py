from pydantic import PrivateAttr
from code_structure.domain.entities.attribute_symbol import AttributeSymbol
from code_structure.domain.entities.method_symbol import MethodSymbol
from code_structure.domain.identities.symbol_ids import ClassId, MethodId, AttributeId
from code_structure.domain.value_objects.location import Location
from foundation.building_blocks.aggregate_root import AggregateRoot
from foundation.common_types.fqns.fqn import ClassFqn


class ClassSymbol(AggregateRoot[ClassId]):
    name: str
    fqn: ClassFqn
    location: Location
    
    _methods: dict[MethodId, MethodSymbol] = PrivateAttr(default_factory=dict)
    _attributes: dict[AttributeId, AttributeSymbol] = PrivateAttr(default_factory=dict)