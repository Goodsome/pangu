import caseconverter
from codegen.shared.domain.value_objects.naming_string import NamingString


class MacroString(NamingString):

    def __new__(cls, value: str):
        converted = caseconverter.macrocase(value)
        return super().__new__(cls, converted)
