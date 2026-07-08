from foundation.building_blocks.value_object import ValueObject
from code_structure.domain.value_objects.parsed_reference import ParsedReference


class ParsedVariable(ValueObject):
    name: str
    references: list[ParsedReference]
