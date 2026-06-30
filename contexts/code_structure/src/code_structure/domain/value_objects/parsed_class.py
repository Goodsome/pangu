from code_structure.domain.value_objects.parsed_attribute import ParsedAttribute
from code_structure.domain.value_objects.parsed_method import ParsedMethod
from foundation.building_blocks.value_object import ValueObject


class ParsedClass(ValueObject):
    name: str
    
    attributes: list[ParsedAttribute]
    methods: list[ParsedMethod]