from typing import ClassVar

from pydantic import ConfigDict, Field

from d4_leaderboard.domain.value_objects.skill import Skill
from foundation.building_blocks.value_object import ValueObject


class SkillBuild(ValueObject):
    """技能组合 build 签名值对象

    以技能 codename 的有序集合标识一个 build, 与技能栏顺序无关;
    暂不纳入强化选择 (modifiers), 留作后续扩展。
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    codenames: tuple[str, ...] = Field(..., description="排序去重后的技能代号")

    @classmethod
    def from_skills(cls, skills: list[Skill]) -> "SkillBuild | None":
        """技能列表为空时返回 None, 表示该条目无 build 签名"""
        codenames = sorted({s.codename for s in skills})
        if not codenames:
            return None
        return cls(codenames=tuple(codenames))

    @property
    def key(self) -> str:
        """持久化/过滤用的规范串, 如 'a+b+c'"""
        return "+".join(self.codenames)

    @classmethod
    def from_key(cls, key: str) -> "SkillBuild":
        return cls(codenames=tuple(key.split("+")))
