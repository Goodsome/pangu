"""暗黑破坏神 4 玩家配置查看器 (PlayerConfigScreen) 页面对象模型。"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, override

from client_core import AutoCalibratingScreen, ImageFrame, RelativeRegion
from d4_client.config.leaderboard import LeaderboardLayoutConfig
from d4_types.enums.player_class import PlayerClass

if TYPE_CHECKING:
    from d4_client.screens.leaderboard import LeaderboardScreen

logger = logging.getLogger(__name__)


SECOND_ROW_EQUIPMENTS_NUMBER: dict[PlayerClass, int] = {
    PlayerClass.BARBARIAN: 4,
    PlayerClass.NECROMANCER: 2,
    PlayerClass.SORCERER: 2,
    PlayerClass.ROGUE: 3,
    PlayerClass.DRUID: 2,
    PlayerClass.SPIRITBORN: 1,
    PlayerClass.PALADIN: 2,
    PlayerClass.WARLOCK: 1,
}


@dataclass(kw_only=True)
class PlayerConfigScreen(AutoCalibratingScreen):
    """暗黑破坏神 4 玩家配置查看器页面对象。

    负责：
    - 点击各类槽位（装备/技能/护身符）
    - 结合 LeaderboardLayoutConfig 动态解算 RelativeRegion
    - 截取 tooltip 预览区图像并使用内部持有的绝对状态保存
    - 关闭配置页回到天梯榜
    """

    player_class: PlayerClass
    page: int
    row: int
    screen_name: str = "PlayerConfigScreen"

    @property
    def config(self) -> LeaderboardLayoutConfig:
        """天梯榜与玩家配置页强类型相对物理布局配置。"""
        return LeaderboardLayoutConfig()

    # ------------------------------------------------------------------
    # 页面状态检测
    # ------------------------------------------------------------------

    @override
    async def is_visible(self) -> bool:
        """通过检测"配置查看器"标题文字判断当前是否处于配置查看页。"""
        result = await self.locate_element(
            element_key="title",
            target_text="配",
            roi=self.config.config_viewer_title_roi,
        )
        return result is not None

    # ------------------------------------------------------------------
    # 装备 (Equipment) 槽位 ROI 与截图
    # ------------------------------------------------------------------

    def get_equipment_slot_count(self) -> int:
        """获取当前职业的装备槽位总数量（第一排 8 个 + 第二排依据职业决定）。"""
        return 8 + SECOND_ROW_EQUIPMENTS_NUMBER[self.player_class]

    def get_equipment_slot_roi(self, slot_index: int) -> RelativeRegion:
        """计算当前职业及槽位索引的装备格子 RelativeRegion。

        第一排固定 8 个装备，第二排由职业决定（1-4个），装备格子大小与第一排一致，且第二排居中。
        """
        second_row_count = SECOND_ROW_EQUIPMENTS_NUMBER[self.player_class]
        total_slots = 8 + second_row_count

        if slot_index < 0 or slot_index >= total_slots:
            raise IndexError(
                f"装备槽索引 {slot_index} 超出有效范围 [0, {total_slots - 1}]"
            )

        eq_roi = self.config.equipment_roi
        slot_w = eq_roi.width / 8.0
        slot_h = eq_roi.height / 2.0

        if slot_index < 8:
            col = slot_index
            x = eq_roi.x + col * slot_w
            y = eq_roi.y
        else:
            k = slot_index - 8
            row2_start_x = eq_roi.x + (eq_roi.width - second_row_count * slot_w) / 2.0
            x = row2_start_x + k * slot_w
            y = eq_roi.y + slot_h

        return RelativeRegion(x=x, y=y, width=slot_w, height=slot_h)

    def get_equipment_tooltip_roi(self, slot_roi: RelativeRegion) -> RelativeRegion:
        """根据装备格子的 RelativeRegion，计算对应的装备详细 tooltip RelativeRegion。

        01 号装备 tooltip 区域为 self.config.equipment_01_roi，其相对于装备格子的偏移是固定的。
        """
        eq_roi = self.config.equipment_roi
        slot_01_x = eq_roi.x
        slot_01_y = eq_roi.y

        offset_x = self.config.equipment_01_roi.x - slot_01_x
        offset_y = self.config.equipment_01_roi.y - slot_01_y

        return RelativeRegion(
            x=slot_roi.x + offset_x,
            y=slot_roi.y + offset_y,
            width=self.config.equipment_01_roi.width,
            height=self.config.equipment_01_roi.height,
        )

    async def capture_equipment_slot(
        self,
        slot_index: int,
    ) -> ImageFrame:
        """点击并截取指定装备槽位的 tooltip 图像帧。"""
        slot_roi = self.get_equipment_slot_roi(slot_index)

        await self.window.mouse_click(point=slot_roi.center)
        await asyncio.sleep(0.5)

        tooltip_roi = self.get_equipment_tooltip_roi(slot_roi)
        return await self.window.capture(region=tooltip_roi, refresh=True)

    # ------------------------------------------------------------------
    # 技能 (Skill) 槽位 ROI 与截图
    # ------------------------------------------------------------------

    def get_skill_slot_count(self) -> int:
        """获取技能槽位总数量（固定 1 排 6 个技能）。"""
        return 6

    def get_skill_slot_roi(self, slot_index: int) -> RelativeRegion:
        """计算 1 排 6 个技能中指定槽位索引的 RelativeRegion。"""
        if slot_index < 0 or slot_index >= 6:
            raise IndexError(f"技能槽索引 {slot_index} 超出有效范围 [0, 5]")

        sk_roi = self.config.skill_roi
        slot_w = sk_roi.width / 6.0
        slot_h = sk_roi.height

        x = sk_roi.x + slot_index * slot_w
        y = sk_roi.y

        return RelativeRegion(x=x, y=y, width=slot_w, height=slot_h)

    def get_skill_tooltip_roi(self, slot_roi: RelativeRegion) -> RelativeRegion:
        """根据技能格子的 RelativeRegion，计算对应的技能详细 tooltip RelativeRegion。"""
        sk_roi = self.config.skill_roi
        slot_01_x = sk_roi.x
        slot_01_y = sk_roi.y

        offset_x = self.config.skill_01_roi.x - slot_01_x
        offset_y = self.config.skill_01_roi.y - slot_01_y

        return RelativeRegion(
            x=slot_roi.x + offset_x,
            y=slot_roi.y + offset_y,
            width=self.config.skill_01_roi.width,
            height=self.config.skill_01_roi.height,
        )

    async def capture_skill_slot(
        self,
        slot_index: int,
    ) -> ImageFrame:
        """点击并截取指定技能槽位的 tooltip 图像帧。"""
        slot_roi = self.get_skill_slot_roi(slot_index)

        await self.window.mouse_click(point=slot_roi.center)
        await asyncio.sleep(0.5)

        tooltip_roi = self.get_skill_tooltip_roi(slot_roi)
        return await self.window.capture(region=tooltip_roi, refresh=True)

    # ------------------------------------------------------------------
    # 护身符 (Talisman) 槽位 ROI 与截图
    # ------------------------------------------------------------------

    def get_talisman_slot_count(self) -> int:
        """获取护身符槽位总数量（固定 1 排 7 个护身符）。"""
        return 7

    def get_talisman_slot_roi(self, slot_index: int) -> RelativeRegion:
        """计算 1 排 7 个护身符中指定槽位索引的 RelativeRegion。"""
        if slot_index < 0 or slot_index >= 7:
            raise IndexError(f"护身符槽索引 {slot_index} 超出有效范围 [0, 6]")

        t_roi = self.config.talismans_roi
        slot_w = t_roi.width / 7.0
        slot_h = t_roi.height

        x = t_roi.x + slot_index * slot_w
        y = t_roi.y

        return RelativeRegion(x=x, y=y, width=slot_w, height=slot_h)

    def get_talisman_tooltip_roi(self, slot_roi: RelativeRegion) -> RelativeRegion:
        """根据护身符格子的 RelativeRegion，计算对应的护身符详细 tooltip RelativeRegion。"""
        t_roi = self.config.talismans_roi
        slot_01_x = t_roi.x
        slot_01_y = t_roi.y

        offset_x = self.config.talismans_01_roi.x - slot_01_x
        offset_y = self.config.talismans_01_roi.y - slot_01_y

        return RelativeRegion(
            x=slot_roi.x + offset_x,
            y=slot_roi.y + offset_y,
            width=self.config.talismans_01_roi.width,
            height=self.config.talismans_01_roi.height,
        )

    async def capture_talisman_slot(
        self,
        slot_index: int,
    ) -> ImageFrame:
        """点击并截取指定护身符槽位的 tooltip 图像帧。"""
        slot_roi = self.get_talisman_slot_roi(slot_index)

        await self.window.mouse_click(point=slot_roi.center)
        await asyncio.sleep(0.5)

        tooltip_roi = self.get_talisman_tooltip_roi(slot_roi)
        return await self.window.capture(region=tooltip_roi, refresh=True)

    # ------------------------------------------------------------------
    # 关闭配置页
    # ------------------------------------------------------------------

    async def close(self) -> LeaderboardScreen:
        """点击右上角关闭按钮，等待返回天梯榜页面。"""
        from d4_client.screens.leaderboard import LeaderboardScreen

        close_point = self.config.close_config_viewer_roi.center
        await self.window.mouse_click(point=close_point)

        screen = LeaderboardScreen(
            window=self.window,
            current_class=self.player_class,
            current_page=self.page,
            current_row=self.row
        )
        await screen.wait_until_visible()
        return screen
