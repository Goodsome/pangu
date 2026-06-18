import re
from typing import Any
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema

_FQN_PATTERN = r"[a-zA-Z0-9_.]+(?:::[a-zA-Z0-9_]+(?:<[a-zA-Z0-9_]+>)?)*"

_CLASS_TYPE = r"(?:<(?:\w+(?:\.\w+)*::)?\w+>(?:\.<\w+>)?)"

SEP = r"[,|]+"
_L1_internal = rf"{_CLASS_TYPE}(?:{SEP}{_CLASS_TYPE})*"
L1_full = rf"{_CLASS_TYPE}\[{_L1_internal}\]"

L2_element = rf"(?:{L1_full}|{_CLASS_TYPE})"
L2_internal = rf"{L2_element}(?:{SEP}{L2_element})*"
L2_full = rf"{_CLASS_TYPE}\[{L2_internal}\]"

L3_element = rf"(?:{L2_full}|{L1_full}|{_CLASS_TYPE})"
L3_internal = rf"{L3_element}(?:{SEP}{L3_element})*"
L3_full = rf"{_CLASS_TYPE}\[{L3_internal}\]"

_GENERIC_TYPE = rf"(?:{L3_full}|{L2_full}|{L1_full})"

_UNION_TYPE = rf"({_CLASS_TYPE}|{_GENERIC_TYPE})(?:\|({_GENERIC_TYPE}|{_CLASS_TYPE}))+"

_SUPPORT_PATTERNS = [
    re.compile(rf"^{_FQN_PATTERN}$"),
    re.compile(rf"^{_CLASS_TYPE}$"),
    re.compile(rf"^{_UNION_TYPE}$"),
    re.compile(rf"^{_GENERIC_TYPE}$")
]

class Fqn(str):
    """支持任意深度、统一处理模块与符号层级的 FQN 强类型字符串。 格式要求：module_path[::symbol_1][::symbol_2]..."""

    @classmethod
    def _match_patterns(cls, value: str) -> bool:
        for pattern in _SUPPORT_PATTERNS:
            if pattern.match(value):
                return True
        return False

    def __new__(cls, value: str) -> Fqn:
        if cls._match_patterns(value):
            return super().__new__(cls, value)
        raise ValueError(f"Invalid FQN format: {value}")

    @property
    def context(self) -> str:
        return self.parts[0]

    @property
    def identify(self) -> str:
        _, identify = self.split("::", maxsplit=1)
        return identify

    @property
    def module_fqn(self) -> Fqn:
        """获取纯模块路径（第一个 :: 之前的部分）"""
        return Fqn(self.split("::")[0])

    @property
    def is_module(self) -> bool:
        return "::" not in self

    @property
    def parent_fqn(self) -> Fqn:
        """
        获取上一层路径。
        逻辑：优先从右侧查找 `::` 进行拆分；如果没有 `::`，则从右侧查找 `.` 进行拆分。
        如果是顶级模块（如 "codegen"），没有父级，返回 None。
        """
        if "::" in self:
            return Fqn(self.rsplit("::", 1)[0])
        if "." in self:
            return Fqn(self.rsplit(".", 1)[0])
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
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls._validate, core_schema.str_schema()
        )

    @classmethod
    def _validate(cls, input_value: str) -> Fqn:
        if cls._match_patterns(input_value):
            return cls(input_value)
        raise ValueError(f"Invalid FQN format: {input_value}")
