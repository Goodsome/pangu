import caseconverter
import re
from codegen.shared.domain.value_objects.naming_string import NamingString


class SnakeString(NamingString):

    def __new__(cls, value: str):
        match = re.match("^(_*)(.*?)(_*)$", value)
        prefix, content, suffix = match.groups()
        converted = caseconverter.snakecase(content)
        return super().__new__(cls, f"{prefix}{converted}{suffix}")
