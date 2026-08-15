"""榜单记录 build 数据镜像值对象。

以 d4_leaderboard ``CreateEntryRequest`` 的 wire 契约为蓝本的镜像 VO
(anti-corruption 镜像层): d4_injestion 不依赖 d4_leaderboard 包, 但注入
payload 的字段名/类型/枚举值与其值对象 (Equipment/Skill/ParagonBoard/
TalismanSnapshot 及嵌套结构) 严格对齐, 调整契约时需双向同步。

字段语义详见 d4_leaderboard 对应值对象; ``slot`` 为装备槽位代码 (int,
对应服务端 EquipmentSlot IntEnum 的数值), ``rarity`` 为稀有度枚举。
"""

from __future__ import annotations

from enum import StrEnum
from typing import ClassVar, override

from pydantic import ConfigDict, Field

from foundation.building_blocks.value_object import ValueObject


class EquipmentRarity(StrEnum):
    """装备稀有度 (镜像 d4_leaderboard EquipmentRarity)。"""

    NORMAL = "Normal"
    MAGIC = "Magic"
    RARE = "Rare"
    LEGENDARY = "Legendary"
    UNIQUE = "Unique"
    MYTHIC_UNIQUE = "Mythic Unique"
    MYTHIC = "Mythic"
    SET = "Set"

    @classmethod
    @override
    def _missing_(cls, value: object) -> EquipmentRarity | None:
        """容忍大小写/空格差异, 与服务端解析策略一致。"""
        if isinstance(value, str):
            normalized = value.lower().replace(" ", "")
            for member in cls:
                if member.value.lower().replace(" ", "") == normalized:
                    return member
        return None


# ---------------------------------------------------------------------------
# 装备
# ---------------------------------------------------------------------------
class Affix(ValueObject):
    """装备词缀 / 属性行。"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    affix_id: int | None = Field(default=None, description="词缀唯一/SNO ID")
    codename: str = Field(..., description="词缀代号")
    stat_type: str = Field(..., description="属性描述文本")
    is_greater: bool = Field(default=False, description="是否为太古词缀")
    is_temper: bool = Field(default=False, description="是否为回粹词缀")
    is_rerolled: bool = Field(default=False, description="是否为重洗词缀")
    is_transfigured: bool = Field(default=False, description="是否为魔改词缀")
    is_masterwork_crit: bool = Field(default=False, description="是否触发精炼重击")


class Socket(ValueObject):
    """装备插槽 (宝石/符文)。"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    id: int = Field(..., description="插槽嵌入物 ID")
    kind: str = Field(..., description="插槽种类: gem/rune")
    codename: str = Field(..., description="插槽物代号")


class AspectPower(ValueObject):
    """传奇威能 / 专属特效。"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    id: int = Field(..., description="威能/特效 ID")
    codename: str = Field(..., description="威能代号")
    category: int = Field(default=0, description="威能类别代码")
    is_transfigured: bool = Field(default=False, description="是否变异")


class Equipment(ValueObject):
    """单件装备快照。"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    item_id: int = Field(..., description="物品唯一/类别 ID")
    codename: str = Field(..., description="装备程序代号")
    slot: int = Field(..., description="装备槽位代码 (服务端 EquipmentSlot 数值)")
    base_type: str = Field(..., description="基础部位类型")
    rarity: EquipmentRarity = Field(..., description="稀有度")
    item_power: int = Field(..., ge=0, description="物品强度")
    is_ancestral: bool = Field(default=False, description="是否远古装备")
    statlines: list[Affix] = Field(default_factory=list, description="词缀列表")
    sockets: list[Socket] = Field(default_factory=list, description="插槽列表")
    aspect_power: AspectPower | None = Field(default=None, description="传奇威能/特效")


# ---------------------------------------------------------------------------
# 技能
# ---------------------------------------------------------------------------
class SkillModifier(ValueObject):
    """技能强化/变体选项。"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    name: str = Field(..., description="选项强化名称")
    is_main: bool = Field(default=False, description="是否为主分支选项")
    bit: int | None = Field(default=None, description="标志位 bit")


class Skill(ValueObject):
    """技能快照 (含强化/变体选项)。"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    sno: int = Field(..., description="技能 SNO ID")
    codename: str = Field(..., description="技能代号")
    name: str = Field(..., description="技能名称")
    modifiers: list[SkillModifier] = Field(
        default_factory=list, description="强化/变体选项列表"
    )


# ---------------------------------------------------------------------------
# 巅峰
# ---------------------------------------------------------------------------
class ParagonGlyph(ValueObject):
    """巅峰雕文。"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    sno: int = Field(..., description="雕文 SNO ID")
    name: str = Field(..., description="雕文显示名称")


class ParagonBoard(ValueObject):
    """巅峰盘。"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    sno: int = Field(..., description="巅峰盘 SNO ID")
    codename: str = Field(..., description="巅峰盘代号")
    legendary_node: str | None = Field(default=None, description="激活的传奇节点名称")
    glyph: ParagonGlyph | None = Field(default=None, description="盘上嵌入的雕文")


# ---------------------------------------------------------------------------
# 护身符
# ---------------------------------------------------------------------------
class TalismanAffix(ValueObject):
    """护符/护印词缀。"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    codename: str = Field(..., description="词缀代号")
    stat_type: str = Field(..., description="属性描述文本")
    is_greater: bool = Field(default=False, description="是否为大号词缀")
    is_mythic: bool = Field(default=False, description="是否为神话词缀")
    is_set_bonus: bool = Field(default=False, description="是否为套装奖励词缀")


class TalismanSeal(ValueObject):
    """护印 (Seal)。"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    codename: str = Field(..., description="护印代号")
    name: str = Field(..., description="护印显示名")
    rarity: EquipmentRarity = Field(..., description="稀有度")
    statlines: list[TalismanAffix] = Field(default_factory=list, description="词缀列表")


class TalismanCharm(ValueObject):
    """护身符 (Charm)。"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    codename: str = Field(..., description="护身符代号")
    name: str = Field(..., description="护身符显示名")
    rarity: EquipmentRarity = Field(..., description="稀有度")
    set_name: str | None = Field(default=None, description="所属套装名称")
    statlines: list[TalismanAffix] = Field(default_factory=list, description="词缀列表")


class TalismanSnapshot(ValueObject):
    """护符系统完整快照。"""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

    seal: TalismanSeal | None = Field(default=None, description="佩戴的护印")
    charms: list[TalismanCharm] = Field(
        default_factory=list, description="佩戴的护身符列表"
    )
