"""helltides 单条 run 详情值对象 (GET /api/tower/getRun 返回)。

外部数据防腐蚀层: 以强类型承接第三方 JSON, 嵌套结构 (装备/词缀/插槽/威能/
技能/巅峰/护身符) 与 d4_leaderboard 领域值对象一一对应, 为后续 build 数据
注入做准备。字段名 snake_case 化, 原始键通过 alias 映射。
"""

from __future__ import annotations

from datetime import datetime
from typing import ClassVar

from pydantic import ConfigDict, Field, field_validator

from foundation.building_blocks.value_object import ValueObject


# ---------------------------------------------------------------------------
# 装备
# ---------------------------------------------------------------------------
class HelltidesStatline(ValueObject):
    """装备词缀。"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, populate_by_name=True)

    affix_id: int | None = Field(default=None, alias="affix_id", description="词缀 ID")
    stat_type: str = Field(..., description="属性描述文本")
    codename: str = Field(..., description="词缀代号")
    category: int = Field(default=0, description="词缀类别代码")
    is_greater: bool = Field(default=False, description="是否太古词缀")
    is_temper: bool = Field(default=False, description="是否回粹词缀")
    is_rerolled: bool = Field(default=False, description="是否重洗词缀")
    is_transfigured: bool = Field(default=False, description="是否魔改词缀")
    is_masterwork_crit: bool = Field(default=False, description="是否触发精炼重击")


class HelltidesSocket(ValueObject):
    """装备插槽 (宝石/符文)。"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, populate_by_name=True)

    id: int = Field(..., description="插槽嵌入物 ID")
    kind: str = Field(..., description="插槽种类 (gem/rune)")
    codename: str = Field(..., description="插槽物代号")


class HelltidesAspectPower(ValueObject):
    """传奇威能 / 专属特效。"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, populate_by_name=True)

    id: int = Field(..., description="威能 ID")
    codename: str = Field(..., description="威能代号")
    category: int = Field(default=0, description="威能类别代码")
    is_transfigured: bool = Field(default=False, description="是否变异")


class HelltidesEquipment(ValueObject):
    """单件装备快照。"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, populate_by_name=True)

    item_id: int = Field(..., description="物品唯一/类别 ID")
    codename: str = Field(..., description="装备程序代号")
    slot: int = Field(..., description="装备槽位代码")
    base_type: str = Field(default="", description="基础部位类型")
    item_type: str = Field(
        default="", description="展示类型 (如 Ancestral Mythic Unique Helm)"
    )
    rarity: str = Field(default="", description="稀有度")
    item_power: int = Field(..., description="物品强度")
    is_ancestral: bool = Field(default=False, description="是否远古装备")
    statlines: list[HelltidesStatline] = Field(
        default_factory=list, description="词缀列表"
    )
    sockets: list[HelltidesSocket] = Field(default_factory=list, description="插槽列表")
    aspect_power: HelltidesAspectPower | None = Field(
        default=None, description="传奇威能/特效"
    )


# ---------------------------------------------------------------------------
# 技能
# ---------------------------------------------------------------------------
class HelltidesSkillModifier(ValueObject):
    """技能强化/变体选项。"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, populate_by_name=True)

    name: str = Field(..., description="选项强化名称")
    is_main: bool = Field(default=False, description="是否为主分支选项")
    bit: int | None = Field(default=None, description="标志位 bit")
    known: bool = Field(default=True, description="是否已解锁")


class HelltidesSkill(ValueObject):
    """技能快照 (skillsSNO 数组元素)。"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, populate_by_name=True)

    name: str = Field(..., description="技能显示名")
    id: str = Field(..., description="技能代号")
    sno: int = Field(..., description="技能 SNO ID")
    modifiers: list[HelltidesSkillModifier] = Field(
        default_factory=list, description="强化/变体选项列表"
    )


# ---------------------------------------------------------------------------
# 巅峰
# ---------------------------------------------------------------------------
class HelltidesParagonGlyph(ValueObject):
    """巅峰雕文 (盘上嵌入形态)。"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, populate_by_name=True)

    level: int = Field(..., description="雕文等级")
    name: str = Field(..., description="雕文名")
    icon: str = Field(default="", description="图标文件名")
    sno: int = Field(..., description="雕文 SNO ID")


class HelltidesParagonBoard(ValueObject):
    """巅峰盘。"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, populate_by_name=True)

    sno: int = Field(..., description="巅峰盘 SNO ID")
    codename: str = Field(..., description="巅峰盘代号")
    slot: int = Field(default=0, description="盘位序号")
    is_starting_board: bool = Field(
        default=False, alias="is_starting_board", description="是否起始盘"
    )
    legendary_node: str | None = Field(default=None, description="激活的传奇节点名")
    legendary_icon: str | None = Field(default=None, description="传奇节点图标")
    glyph: HelltidesParagonGlyph | None = Field(default=None, description="盘上雕文")


class HelltidesParagonBoardGlyph(ValueObject):
    """巅峰雕文 (glyphs 汇总列表形态)。"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, populate_by_name=True)

    sno: int = Field(..., description="雕文 SNO ID")
    name: str = Field(..., description="雕文名")
    level: int = Field(..., description="雕文等级")
    icon: str = Field(default="", description="图标文件名")
    board_slot: int = Field(default=0, description="所在盘位序号")
    board_legendary: str | None = Field(default=None, description="所在盘传奇节点名")


class HelltidesParagon(ValueObject):
    """巅峰系统快照。"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, populate_by_name=True)

    legendary_nodes: list[str] = Field(
        default_factory=list, description="激活的传奇节点名列表"
    )
    boards: list[HelltidesParagonBoard] = Field(
        default_factory=list, description="巅峰盘列表"
    )
    glyphs: list[HelltidesParagonBoardGlyph] = Field(
        default_factory=list, description="雕文汇总列表"
    )


# ---------------------------------------------------------------------------
# 护身符
# ---------------------------------------------------------------------------
class HelltidesTalismanAffix(ValueObject):
    """护符/护印词缀。"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, populate_by_name=True)

    stat_type: str = Field(..., description="属性描述文本")
    codename: str = Field(..., description="词缀代号")
    is_greater: bool = Field(default=False, description="是否大号词缀")
    is_mythic: bool = Field(default=False, description="是否神话词缀")
    is_set_bonus: bool = Field(default=False, description="是否套装奖励词缀")


class HelltidesTalismanSetBonus(ValueObject):
    """护符套装奖励条目。"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, populate_by_name=True)

    pieces: int = Field(..., description="触发所需件数")
    desc: str = Field(default="", description="奖励描述 (含 HTML 标签)")
    sno: int = Field(..., description="奖励 SNO ID")


class HelltidesTalismanSet(ValueObject):
    """护符套装信息。"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, populate_by_name=True)

    name: str | None = Field(default=None, description="套装名")
    bonuses: list[HelltidesTalismanSetBonus] = Field(
        default_factory=list, description="套装奖励列表"
    )


class HelltidesTalismanSeal(ValueObject):
    """护印 (Seal)。"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, populate_by_name=True)

    codename: str = Field(..., description="护印代号")
    name: str = Field(..., description="护印显示名")
    rarity: str = Field(..., description="稀有度")
    statlines: list[HelltidesTalismanAffix] = Field(
        default_factory=list, description="词缀列表"
    )
    greater_affix_count: int = Field(
        default=0, alias="greaterAffixCount", description="大号词缀数量"
    )
    icon_url: str = Field(default="", alias="iconUrl", description="图标 URL")


class HelltidesTalismanCharm(ValueObject):
    """护身符 (Charm/神符)。"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, populate_by_name=True)

    codename: str = Field(..., description="护身符代号")
    name: str = Field(..., description="护身符显示名")
    rarity: str = Field(..., description="稀有度")
    power: str | None = Field(default=None, description="附带威能代号")
    set: HelltidesTalismanSet | None = Field(default=None, description="所属套装")
    statlines: list[HelltidesTalismanAffix] = Field(
        default_factory=list, description="词缀列表"
    )


class HelltidesTalismans(ValueObject):
    """护符系统完整快照。"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, populate_by_name=True)

    seal: HelltidesTalismanSeal | None = Field(default=None, description="佩戴的护印")
    charms: list[HelltidesTalismanCharm] = Field(
        default_factory=list, description="佩戴的护身符列表"
    )


# ---------------------------------------------------------------------------
# 杂项时间结构
# ---------------------------------------------------------------------------
class HelltidesRunTime(ValueObject):
    """runTime 结构化用时。"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, populate_by_name=True)

    minutes: int = Field(..., description="分钟")
    seconds: int = Field(..., description="秒")
    milliseconds: int = Field(..., description="毫秒")


class HelltidesSyncedAt(ValueObject):
    """syncedAt 时间戳 (Firestore 风格)。"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, populate_by_name=True)

    seconds: int = Field(..., alias="_seconds", description="epoch 秒")
    nanoseconds: int = Field(..., alias="_nanoseconds", description="纳秒部分")


# ---------------------------------------------------------------------------
# Run 详情
# ---------------------------------------------------------------------------
class HelltidesRunDetail(ValueObject):
    """单条 run 完整详情 (含 build 数据)。"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, populate_by_name=True)

    id: str = Field(..., description="run 的 uuid")
    run_uuid: str = Field(default="", description="run uuid")
    slot_id: str = Field(default="", alias="slot_id", description="槽位 ID")
    player_name: str = Field(..., alias="playerName", description="玩家名称")
    battle_tag: str = Field(default="", description="玩家 battle tag")
    normalized_battle_tag: str = Field(default="", description="规范化 battle tag")
    player_class: str = Field(..., alias="class", description="职业 (小写)")
    tier: int = Field(..., description="大秘境层数")
    run_time_ms: int = Field(..., alias="run_time_ms", description="通关用时 (毫秒)")
    run_time: HelltidesRunTime | None = Field(
        default=None, alias="runTime", description="结构化用时"
    )
    run_created_at: datetime | None = Field(
        default=None, alias="runCreatedAt", description="run 创建时间"
    )
    synced_at: HelltidesSyncedAt | None = Field(
        default=None, alias="syncedAt", description="数据同步时间"
    )
    platform: str = Field(default="", description="平台")
    hardcore: bool = Field(default=False, description="是否硬核")
    ssf: bool = Field(default=False, description="是否单人模式")
    active: bool = Field(default=True, description="是否有效记录")
    entity_id: str = Field(default="", description="实体 ID")
    owner_hero_id: str = Field(default="", description="所属英雄 ID")
    client_build_version: str = Field(default="", description="客户端版本")
    powers: list[str] = Field(default_factory=list, description="威能代号列表")
    skills: list[str] = Field(default_factory=list, description="技能代号列表")
    skills_sno: list[HelltidesSkill] = Field(
        default_factory=list, alias="skillsSNO", description="技能快照列表"
    )
    paragon_ids: list[int] = Field(
        default_factory=list, alias="paragonIDs", description="巅峰 SNO 列表"
    )
    paragon: HelltidesParagon | None = Field(default=None, description="巅峰快照")
    talisman_ids: list[str] = Field(
        default_factory=list, alias="talismanIDs", description="护身符代号列表"
    )
    talismans: HelltidesTalismans | None = Field(default=None, description="护符快照")
    equipment: list[HelltidesEquipment] = Field(
        default_factory=list, description="装备列表"
    )

    @field_validator(
        "powers",
        "skills",
        "skills_sno",
        "paragon_ids",
        "talisman_ids",
        "equipment",
        mode="before",
    )
    @classmethod
    def _drop_none_entries(cls, value: object) -> object:
        """过滤列表中的 null 空槽位 (与 HelltidesRow 保持一致的防腐蚀策略)。"""
        if isinstance(value, list):
            return [item for item in value if item is not None]
        return value
