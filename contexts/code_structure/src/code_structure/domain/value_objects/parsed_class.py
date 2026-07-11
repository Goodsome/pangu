from code_structure.domain.value_objects.parsed_function import ParsedFunction
from code_structure.domain.value_objects.parsed_reference import ParsedReference
from code_structure.domain.value_objects.parsed_variable import ParsedVariable
from foundation.building_blocks.value_object import ValueObject


class ParsedClass(ValueObject):
    name: str

    variables: list[ParsedVariable]
    functions: list[ParsedFunction]
    references: list[ParsedReference]
