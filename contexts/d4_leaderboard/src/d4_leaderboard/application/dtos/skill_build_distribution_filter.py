from pydantic import BaseModel, Field

from d4_types.enums.player_class import PlayerClass


class SkillBuildDistributionFilter(BaseModel):
    """技能组合分布统计条件；player_class 为 None 时表示不限制。"""

    player_class: PlayerClass | None = None
    min_tier: int = Field(default=1, ge=1, le=150)
