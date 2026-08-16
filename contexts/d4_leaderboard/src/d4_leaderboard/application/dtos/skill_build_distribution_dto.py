from pydantic import BaseModel, Field

from d4_types.enums.player_class import PlayerClass


class SkillBuildItem(BaseModel):
    """单个技能组合 build 的使用频次"""

    build_key: str = Field(..., description="build 签名 (排序 codename 以 '+' 拼接)")
    skills: list[str] = Field(..., description="构成 build 的技能代号列表")
    count: int = Field(..., description="使用该 build 的条目数")
    percentage: float = Field(..., description="占命中条目数的百分比 (0-100)")


class SkillBuildDistributionDto(BaseModel):
    """技能组合 build 分布统计结果"""

    player_class: PlayerClass | None = None
    min_tier: int = Field(default=1)

    entry_count: int = Field(..., description="命中的榜单条目数 (含无技能条目)")
    build_count: int = Field(..., description="去重后的 build 数")

    items: list[SkillBuildItem] = Field(default_factory=list)
