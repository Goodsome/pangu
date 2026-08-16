from pydantic import BaseModel, Field

from d4_types.enums.player_class import PlayerClass
from d4_leaderboard.domain.enums.equipment_slot import EquipmentSlot


class AffixDistributionItem(BaseModel):
    """单个词缀在指定过滤条件下的出现频次"""

    codename: str = Field(..., description="词缀代号")
    stat_type: str = Field(..., description="属性描述文本")
    count: int = Field(..., description="出现的装备件数")
    percentage: float = Field(..., description="占分母的百分比 (0-100)")


class AffixDistributionDto(BaseModel):
    """词缀选择分布统计结果

    innate / temper / transfigured 三类互斥:
    回火、嬗变各自单独统计, 其余为装备自带词缀;
    masterwork_crit 独立成表: 精炼可点在任意词缀上 (含回火), 故跨类别汇总。
    """

    player_class: PlayerClass | None = None
    slot: EquipmentSlot | None = None
    min_tier: int = 1
    build_key: str | None = None

    entry_count: int = Field(..., description="命中的榜单条目数")
    item_count: int = Field(
        ..., description="命中的装备件数 (innate/temper/transfigured 的分母)"
    )
    masterwork_item_count: int = Field(
        ..., description="带精炼标记的装备件数 (masterwork_crit 的分母)"
    )

    innate: list[AffixDistributionItem] = Field(default_factory=list)
    temper: list[AffixDistributionItem] = Field(default_factory=list)
    transfigured: list[AffixDistributionItem] = Field(default_factory=list)
    masterwork_crit: list[AffixDistributionItem] = Field(default_factory=list)
