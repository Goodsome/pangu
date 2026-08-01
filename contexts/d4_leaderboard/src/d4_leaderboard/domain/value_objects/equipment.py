from typing import ClassVar

from pydantic import ConfigDict, Field

from d4_leaderboard.domain.enums.equipment_base_type import EquipmentBaseType
from d4_leaderboard.domain.enums.equipment_rarity import EquipmentRarity
from d4_leaderboard.domain.enums.equipment_slot import EquipmentSlot
from d4_leaderboard.domain.value_objects.affix import Affix
from d4_leaderboard.domain.value_objects.aspect_power import AspectPower
from d4_leaderboard.domain.value_objects.socket import Socket
from foundation.building_blocks.value_object import ValueObject


class Equipment(ValueObject):
    """玩家单件装备快照值对象"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    item_id: int = Field(..., description="物品唯一/类别 ID")
    codename: str = Field(..., description="装备程序代号")
    slot: EquipmentSlot = Field(..., description="装备槽位枚举")
    base_type: EquipmentBaseType | str = Field(..., description="基础部位类型")
    rarity: EquipmentRarity = Field(..., description="稀有度")
    item_power: int = Field(..., ge=0, description="物品强度")
    is_ancestral: bool = Field(default=False, description="是否远古装备")

    statlines: list[Affix] = Field(default_factory=list, description="词缀列表")
    sockets: list[Socket] = Field(default_factory=list, description="插槽列表")
    aspect_power: AspectPower | None = Field(default=None, description="传奇威能/特效")

    @property
    def display_type(self) -> str:
        """动态生成展示类型名称 (替代冗余的 item_type)"""
        parts: list[str] = []
        if self.is_ancestral:
            parts.append("Ancestral")
        parts.append(str(self.rarity))
        parts.append(str(self.base_type))
        return " ".join(parts)
