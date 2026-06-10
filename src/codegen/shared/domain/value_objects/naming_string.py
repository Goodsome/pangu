from typing import Any
import caseconverter
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema
from pydantic_core.core_schema import CoreSchema


class NamingString(str):
    """基于 case-converter 的增强型字符串"""

    def to_pascal(self) -> str:
        return caseconverter.pascalcase(self)

    def to_snake(self) -> str:
        return caseconverter.snakecase(self)

    def to_kebab(self) -> str:
        return caseconverter.kebabcase(self)

    def to_camel(self) -> str:
        return caseconverter.camelcase(self)

    def to_macro(self) -> str:
        return caseconverter.macrocase(self)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls, core_schema.str_schema()
        )
