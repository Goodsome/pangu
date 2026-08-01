from typing import ClassVar

from pydantic import ConfigDict, Field

from foundation.building_blocks.value_object import ValueObject


class SkillModifier(ValueObject):
    """技能强化/变体选项值对象 (如分支强化项)"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    name: str = Field(..., description="选项强化名称 (如 Full Throttle)")
    is_main: bool = Field(default=False, description="是否为主分支选项")
    bit: int | None = Field(default=None, description="标志位 bit")


class Skill(ValueObject):
    """技能快照值对象 (包含技能及3个选项分支)"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    sno: int = Field(..., description="技能 SNO ID")
    codename: str = Field(..., description="技能代号")
    name: str = Field(..., description="技能名称")
    modifiers: list[SkillModifier] = Field(
        default_factory=list, description="技能的3个强化/变体选项列表"
    )
