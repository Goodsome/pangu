from code_structure.domain.value_objects.parsed_class import ParsedClass
from foundation.building_blocks.value_object import ValueObject
from foundation.common_types.fqns.fqn import ModuleFqn


class ParsedFileModule(ValueObject):
    fqn: ModuleFqn
    
    classes: list[ParsedClass]