import caseconverter
from codegen.shared.domain.value_objects.naming_string import NamingString


class PascalString(NamingString):

    def __new__(cls, value: str):
        converted = caseconverter.pascalcase(value)
        return super().__new__(cls, converted)
