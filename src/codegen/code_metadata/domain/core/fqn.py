import re
from typing import Any, ClassVar

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema


class Fqn(str):
    """支持任意深度、统一处理模块与符号层级的 FQN 强类型字符串。 格式要求：module_path[::symbol_1][::symbol_2]..."""

    _FQN_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"^[a-zA-Z0-9_.]+(?:::[a-zA-Z0-9_]+(?:<[a-zA-Z0-9_]+>)?)*$"
    )

    @property
    def module_path(self) -> str:
        """获取纯模块路径（第一个 :: 之前的部分）"""
        return self.split("::")[0]

    @property
    def parent_path(self) -> str | None:
        """
        获取上一层路径。
        逻辑：优先从右侧查找 `::` 进行拆分；如果没有 `::`，则从右侧查找 `.` 进行拆分。
        如果是顶级模块（如 "codegen"），没有父级，返回 None。
        """
        if "::" in self:
            return self.rsplit("::", 1)[0]
        if "." in self:
            return self.rsplit(".", 1)[0]
        return None

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
        # 将所有的 :: 替换为 .，然后统一拆分
        return tuple(self.replace("::", ".").split("."))

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.str_schema(),
        )

    @classmethod
    def _validate(cls, input_value: str) -> Fqn:
        if not cls._FQN_PATTERN.match(input_value):
            raise ValueError(f"Invalid FQN format: {input_value}")
        return cls(input_value)
