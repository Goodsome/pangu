from typing import ClassVar
from foundation.building_blocks.value_object import ValueObject
from pydantic import ConfigDict, Field


class Affix(ValueObject):
    """装备词缀 / 属性行值对象"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    affix_id: int | None = Field(default=None, description="词缀唯一/SNO ID")
    codename: str = Field(..., description="词缀代号")
    stat_type: str = Field(..., description="属性描述文本")

    is_greater: bool = Field(default=False, description="是否为太古词缀")
    is_temper: bool = Field(default=False, description="是否为回火词缀")
    is_rerolled: bool = Field(default=False, description="是否为重洗词缀")
    is_transfigured: bool = Field(default=False, description="是否为嬗变词缀")
    is_masterwork_crit: bool = Field(default=False, description="是否精炼")
