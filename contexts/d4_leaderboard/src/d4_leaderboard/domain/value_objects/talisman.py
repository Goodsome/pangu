from typing import ClassVar

from pydantic import ConfigDict, Field

from d4_leaderboard.domain.enums.equipment_rarity import EquipmentRarity
from foundation.building_blocks.value_object import ValueObject


class TalismanAffix(ValueObject):
    """护符/护印词缀值对象"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    codename: str = Field(..., description="词缀代号")
    stat_type: str = Field(..., description="属性描述文本")
    is_greater: bool = Field(default=False, description="是否为大号词缀")
    is_mythic: bool = Field(default=False, description="是否为神话词缀")
    is_set_bonus: bool = Field(default=False, description="是否为套装奖励词缀")


class TalismanSeal(ValueObject):
    """护印 (Seal) 快照值对象"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    codename: str = Field(..., description="护印代号")
    name: str = Field(..., description="护印显示名称")
    rarity: EquipmentRarity = Field(..., description="稀有度")
    statlines: list[TalismanAffix] = Field(default_factory=list, description="词缀列表")


class TalismanCharm(ValueObject):
    """护身符 (Charm) 快照值对象"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    codename: str = Field(..., description="护身符代号")
    name: str = Field(..., description="护身符显示名称")
    rarity: EquipmentRarity = Field(..., description="稀有度")
    set_name: str | None = Field(default=None, description="所属套装名称")
    statlines: list[TalismanAffix] = Field(default_factory=list, description="词缀列表")


class TalismanSnapshot(ValueObject):
    """护符系统完整快照值对象"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    seal: TalismanSeal | None = Field(default=None, description="佩戴的护印")
    charms: list[TalismanCharm] = Field(
        default_factory=list, description="佩戴的护身符列表"
    )
