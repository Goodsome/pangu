"""helltides 榜单行值对象 (GET /api/tower/getAll 返回数组的元素)。

外部数据防腐蚀层: 以强类型承接第三方 JSON, 字段名 snake_case 化,
camelCase 原始键通过 alias 映射。
"""

from __future__ import annotations

from typing import ClassVar

from pydantic import ConfigDict, Field, field_validator

from foundation.building_blocks.value_object import ValueObject


class HelltidesSkillDetail(ValueObject):
    """榜单行内嵌的技能摘要。"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, populate_by_name=True)

    id: str = Field(..., description="技能代号 (如 lightningstorm)")
    name: str = Field(..., description="技能显示名")
    type: str = Field(default="", description="技能类型 (如 Core)")
    skill_class: str = Field(default="", alias="skillClass", description="所属职业")
    sno: int = Field(..., description="技能 SNO ID")


class HelltidesRow(ValueObject):
    """helltides 榜单单行数据。"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, populate_by_name=True)

    id: str = Field(..., description="run 的 uuid (用于 getRun 查询)")
    rank: int = Field(..., description="全局排名")
    filtered_rank: int = Field(..., alias="filteredRank", description="过滤后排名")
    player_name: str = Field(..., alias="playerName", description="玩家名称")
    battle_tag: str = Field(default="", description="玩家 battle tag")
    player_class: str = Field(..., alias="class", description="职业 (小写, 如 druid)")
    tier: int = Field(..., description="大秘境层数")
    run_time_ms: int = Field(..., alias="run_time_ms", description="通关用时 (毫秒)")
    run_uuid: str = Field(default="", description="run uuid")
    platform: str = Field(default="", description="平台 (pc/playstation/xbox)")
    hardcore: bool = Field(default=False, description="是否硬核")
    ssf: bool = Field(default=False, description="是否单人模式")
    client_build_version: str = Field(default="", description="客户端版本")
    is_top_run_by_class: bool = Field(
        default=False, alias="isTopRunByClass", description="是否该职业最佳记录"
    )
    skills: list[str] = Field(default_factory=list, description="技能代号列表")
    skill_details: list[HelltidesSkillDetail] = Field(
        default_factory=list, alias="skillDetails", description="技能摘要列表"
    )
    paragon_ids: list[int] = Field(
        default_factory=list, alias="paragonIDs", description="巅峰盘/雕文 SNO 列表"
    )
    talisman_ids: list[str] = Field(
        default_factory=list, alias="talismanIDs", description="护身符代号列表"
    )
    powers: list[str] = Field(default_factory=list, description="威能代号列表")

    @field_validator(
        "skills",
        "skill_details",
        "paragon_ids",
        "talisman_ids",
        "powers",
        mode="before",
    )
    @classmethod
    def _drop_none_entries(cls, value: object) -> object:
        """过滤列表中的 null 空槽位 (helltides 用 null 占位空技能槽)。"""
        if isinstance(value, list):
            return [item for item in value if item is not None]
        return value
