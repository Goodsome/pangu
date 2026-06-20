import re
from typing import Any, ClassVar, Self

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema
from pydantic_core.core_schema import no_info_after_validator_function, str_schema



class BaseFqn(str):

    _SUPPORT_PATTERN: ClassVar[re.Pattern[str]] 
    
    @classmethod
    def _match_patterns(cls, value: str) -> bool:
        if cls._SUPPORT_PATTERN.match(value):
            return True
        return False

    def __new__(cls, value: str) -> Self:
        if cls._match_patterns(value):
            return super().__new__(cls, value)
        raise ValueError(f"Invalid FQN format: {value}")

    @property
    def context(self) -> str:
        return self.parts[0]

    @property
    def identify(self) -> str:
        if "::" not in self:
            return self.symbol
        _, identify = self.split("::", maxsplit=1)
        return identify

    @property
    def module_fqn(self) -> Self:
        """获取纯模块路径（第一个 :: 之前的部分）"""
        return self.__class__(self.split("::")[0])

    @property
    def is_module(self) -> bool:
        return "::" not in self

    @property
    def parent_fqn(self) -> Self:
        """
        获取上一层路径。
        逻辑：优先从右侧查找 `::` 进行拆分；如果没有 `::`，则从右侧查找 `.` 进行拆分。
        如果是顶级模块（如 "codegen"），没有父级，返回 None。
        """
        if "::" in self:
            return self.__class__(self.rsplit("::", 1)[0])
        if "." in self:
            return self.__class__(self.rsplit(".", 1)[0])
        raise ValueError(f"Parent fqn not Found: self={self!r}")

    @property
    def symbol(self) -> str:
        """
        获取当前节点的短名称。
        逻辑：取最后一个 `::` 之后的部分；如果没有 `::`，取最后一个 `.` 之后的部分。
        如果是顶级模块，返回其本身。
        """
        if "::" in self:
            return self.rsplit("::", 1)[1]
        if "." in self:
            return self.rsplit(".", 1)[1]
        return str(self)

    @property
    def parts(self) -> tuple[str, ...]:
        """将完整的层级拆解为元组（兼容 . 和 :: 的全路径打平）"""
        return tuple(self.replace("::", ".").split("."))

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return no_info_after_validator_function(
            cls._validate, str_schema()
        )

    @classmethod
    def _validate(cls, input_value: str) -> Self:
        if cls._match_patterns(input_value):
            return cls(input_value)
        raise ValueError(f"Invalid FQN format: {input_value}")


_MODULE_REGEX = r"(?:\w\.)*\w"

class ModuleFqn(BaseFqn):

    _SUPPORT_PATTERN: ClassVar[re.Pattern[str]] = re.compile(rf"^{_MODULE_REGEX}$")