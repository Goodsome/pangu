from code_structure.domain.value_objects.parsed_class import ParsedClass
from code_structure.domain.value_objects.parsed_function import ParsedFunction
from code_structure.domain.value_objects.parsed_variable import ParsedVariable
from code_structure.domain.value_objects.parsed_import import ParsedImport
from foundation.building_blocks.value_object import ValueObject
from foundation.common_types.fqns.fqn import ModuleFqn


class ParsedFileModule(ValueObject):
    fqn: ModuleFqn

    classes: list[ParsedClass]
    functions: list[ParsedFunction]
    variables: list[ParsedVariable]
    imports: list[ParsedImport]
