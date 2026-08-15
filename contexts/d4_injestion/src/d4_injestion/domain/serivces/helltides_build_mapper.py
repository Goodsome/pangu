"""helltides run 详情 build 数据 -> LeaderboardRecord 镜像 VO 映射领域服务。

注意:
  - helltides 原始结构 (HelltidesEquipment 等) 是第三方防腐蚀 VO, 字段比
    注入契约更宽 (如 item_type / category / level / icon 等), 本映射裁剪为
    d4_leaderboard wire 契约所需的镜像 VO (leaderboard_build);
  - ``slot`` 槽位代码与 ``rarity`` 稀有度取值与服务端枚举数值/字符串对齐,
    无法识别的稀有度抛出 ValueError, 由调用方决定跳过或记录。
"""

from __future__ import annotations

from dataclasses import dataclass

from d4_injestion.domain.value_objects.helltides_run_detail import (
    HelltidesAspectPower,
    HelltidesEquipment,
    HelltidesParagonBoard,
    HelltidesRunDetail,
    HelltidesSkill,
    HelltidesSocket,
    HelltidesTalismanAffix,
    HelltidesStatline,
    HelltidesTalismanCharm,
    HelltidesTalismanSeal,
    HelltidesTalismans,
)
from d4_injestion.domain.value_objects.leaderboard_build import (
    Affix,
    AspectPower,
    Equipment,
    EquipmentRarity,
    ParagonBoard,
    ParagonGlyph,
    Skill,
    SkillModifier,
    Socket,
    TalismanAffix,
    TalismanCharm,
    TalismanSeal,
    TalismanSnapshot,
)
from d4_injestion.domain.value_objects.leaderboard_record import LeaderboardRecord


@dataclass
class HelltidesBuildMapper:
    """``HelltidesRunDetail`` build 数据 -> ``LeaderboardRecord`` 回填映射器。"""

    def to_record(
        self,
        record: LeaderboardRecord,
        detail: HelltidesRunDetail,
    ) -> LeaderboardRecord:
        """将 run 详情中的 build 数据映射为镜像 VO 并回填到新 record。

        原 record 保持不变 (frozen), 返回携带 build 数据的新实例。

        Args:
            record: 由榜单行映射出的基础记录。
            detail: 该玩家 run 的完整详情 (GET /api/tower/getRun)。

        Raises:
            ValueError: 稀有度等枚举取值无法映射到注入契约。
        """
        return record.model_copy(
            update={
                "equipment": [self._to_equipment(item) for item in detail.equipment],
                "skills": [self._to_skill(skill) for skill in detail.skills_sno],
                "paragon_boards": [
                    self._to_paragon_board(board)
                    for board in (detail.paragon.boards if detail.paragon else [])
                ],
                "talismans": self._to_talisman_snapshot(detail.talismans),
            },
        )

    def _to_equipment(self, item: HelltidesEquipment) -> Equipment:
        """单件装备映射 (裁剪 item_type 展示字段)。"""
        return Equipment(
            item_id=item.item_id,
            codename=item.codename,
            slot=item.slot,
            base_type=item.base_type,
            rarity=self._to_rarity(item.rarity),
            item_power=item.item_power,
            is_ancestral=item.is_ancestral,
            statlines=[self._to_affix(line) for line in item.statlines],
            sockets=[self._to_socket(socket) for socket in item.sockets],
            aspect_power=(
                self._to_aspect_power(item.aspect_power)
                if item.aspect_power is not None
                else None
            ),
        )

    def _to_rarity(self, raw: str) -> EquipmentRarity:
        """稀有度字符串 -> 镜像枚举 (无法识别时抛 ValueError)。"""
        return EquipmentRarity(raw)

    def _to_affix(self, line: HelltidesStatline) -> Affix:
        """词缀映射 (裁剪 category 类别代码)。"""
        return Affix(
            affix_id=line.affix_id,
            codename=line.codename,
            stat_type=line.stat_type,
            is_greater=line.is_greater,
            is_temper=line.is_temper,
            is_rerolled=line.is_rerolled,
            is_transfigured=line.is_transfigured,
            is_masterwork_crit=line.is_masterwork_crit,
        )

    def _to_socket(self, socket: HelltidesSocket) -> Socket:
        """插槽映射 (kind 透传 gem/rune)。"""
        return Socket(
            id=socket.id,
            kind=socket.kind,
            codename=socket.codename,
        )

    def _to_aspect_power(self, power: HelltidesAspectPower) -> AspectPower:
        """威能/特效映射 (字段一一致)。"""
        return AspectPower(
            id=power.id,
            codename=power.codename,
            category=power.category,
            is_transfigured=power.is_transfigured,
        )

    def _to_skill(self, skill: HelltidesSkill) -> Skill:
        """技能映射: ``id`` -> ``codename`` (裁剪 known)。"""
        return Skill(
            sno=skill.sno,
            codename=skill.id,
            name=skill.name,
            modifiers=[
                SkillModifier(
                    name=modifier.name,
                    is_main=modifier.is_main,
                    bit=modifier.bit,
                )
                for modifier in skill.modifiers
            ],
        )

    def _to_paragon_board(self, board: HelltidesParagonBoard) -> ParagonBoard:
        """巅峰盘映射 (裁剪 slot / legendary_icon / is_starting_board)。"""
        return ParagonBoard(
            sno=board.sno,
            codename=board.codename,
            legendary_node=board.legendary_node,
            glyph=(
                ParagonGlyph(sno=board.glyph.sno, name=board.glyph.name)
                if board.glyph is not None
                else None
            ),
        )

    def _to_talisman_snapshot(
        self, talismans: HelltidesTalismans | None
    ) -> TalismanSnapshot | None:
        """护符快照映射 (裁剪 icon_url / greater_affix_count / 套装 bonuses)。"""
        if talismans is None:
            return None
        return TalismanSnapshot(
            seal=self._to_talisman_seal(talismans.seal),
            charms=[self._to_talisman_charm(charm) for charm in talismans.charms],
        )

    def _to_talisman_seal(
        self, seal: HelltidesTalismanSeal | None
    ) -> TalismanSeal | None:
        """护印映射。"""
        if seal is None:
            return None
        return TalismanSeal(
            codename=seal.codename,
            name=seal.name,
            rarity=self._to_rarity(seal.rarity),
            statlines=[self._to_talisman_affix(line) for line in seal.statlines],
        )

    def _to_talisman_charm(self, charm: HelltidesTalismanCharm) -> TalismanCharm:
        """护身符映射: 套装名取 ``set.name`` (裁剪 power / bonuses)。"""
        return TalismanCharm(
            codename=charm.codename,
            name=charm.name,
            rarity=self._to_rarity(charm.rarity),
            set_name=charm.set.name if charm.set is not None else None,
            statlines=[self._to_talisman_affix(line) for line in charm.statlines],
        )

    def _to_talisman_affix(self, line: HelltidesTalismanAffix) -> TalismanAffix:
        """护符词缀映射 (字段一一致)。"""
        return TalismanAffix(
            codename=line.codename,
            stat_type=line.stat_type,
            is_greater=line.is_greater,
            is_mythic=line.is_mythic,
            is_set_bonus=line.is_set_bonus,
        )
