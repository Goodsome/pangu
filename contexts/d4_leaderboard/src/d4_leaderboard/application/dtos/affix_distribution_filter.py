from pydantic import BaseModel, Field

from d4_types.enums.player_class import PlayerClass
from d4_leaderboard.domain.enums.equipment_slot import EquipmentSlot


class AffixDistributionFilter(BaseModel):
    """词缀分布统计条件；player_class / slot 为 None 时表示不限制。"""

    player_class: PlayerClass | None = None
    slot: EquipmentSlot | None = None
    min_tier: int = Field(default=100, ge=1, le=150)
