import caseconverter
import re
from foundation.common_types.naming_string import NamingString


class SnakeString(NamingString):
    def __new__(cls, value: str):
        match = re.match("^(_*)(.*?)(_*)$", value)
        if match:
            prefix, content, suffix = match.groups()
        else:
            prefix = ""
            content = value
            suffix = ""
        converted = caseconverter.snakecase(content)
        return super().__new__(cls, f"{prefix}{converted}{suffix}")
