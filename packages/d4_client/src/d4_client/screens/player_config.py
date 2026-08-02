"""暗黑破坏神 4 玩家配置查看器 (PlayerConfigScreen) 页面对象模型。"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, override

from d4_client.config.leaderboard import (
    LeaderboardConfig,
    LeaderboardLayoutConfig,
    PlayerConfigLayoutConfig,
    SlotConfig,
    load_leaderboard_config,
)
from d4_client.models import ImageFrame, Region
from d4_client.screens.base import AutoCalibratingScreen

if TYPE_CHECKING:
    from d4_client.screens.leaderboard import LeaderboardScreen

logger = logging.getLogger(__name__)


@dataclass
class PlayerConfigScreen(AutoCalibratingScreen):
    """暗黑破坏神 4 玩家配置查看器页面对象。

    负责：
    - 鼠标悬停各类槽位（装备/技能/巅峰/护身符）
    - 截取左侧 tooltip 预览区图像
    - 关闭配置页回到天梯榜
    """

    screen_name: str = "PlayerConfigScreen"

    @property
    def config(self) -> LeaderboardLayoutConfig:
        return LeaderboardLayoutConfig()

    @property
    def _layout(self) -> PlayerConfigLayoutConfig:
        return load_leaderboard_config().player_config

    # ------------------------------------------------------------------
    # 页面状态检测
    # ------------------------------------------------------------------

    @override
    async def is_visible(self) -> bool:
        """通过检测"配置查看器"标题文字判断当前是否处于配置查看页。"""
        result = await self.window.find_text(
            target_text="配置查看器",
            roi=self.config.config_viewer_title_roi,
        )
        return result is not None

    # ------------------------------------------------------------------
    # 通用槽位截图（内部）
    # ------------------------------------------------------------------

    async def _capture_slot(self, slot: SlotConfig) -> ImageFrame:
        """移动鼠标到槽位悬停坐标，等待 tooltip 渲染后截取预览区图像。"""
        await self.window.mouse_move(point=slot.hover)

        # 等待 tooltip 渲染（时间由上层 capture_task.yaml 控制，此处给基础等待）
        await asyncio.sleep(0.1)

        tt = self._layout.tooltip
        if tt.strategy == "fixed_left":
            region = tt.fixed_region
        else:
            # near_cursor: 以悬停点为基准计算截图区域
            ox, oy = tt.cursor_offset
            cw, ch = tt.cursor_size
            region = Region(
                x=slot.hover.x + ox,
                y=slot.hover.y + oy,
                width=cw,
                height=ch,
            )

        logger.debug(
            "[PlayerConfigScreen] 悬停槽位 '%s'，截取区域 %s", slot.name, region
        )
        return await self.window.capture(region=region)

    # ------------------------------------------------------------------
    # 各类槽位公开截图接口
    # ------------------------------------------------------------------

    async def capture_equipment_slot(self, slot_index: int) -> ImageFrame:
        """悬停并截取指定装备槽位的 tooltip 图像。

        Args:
            slot_index: 装备槽索引，范围 0 ~ len(equipment_slots)-1。
        """
        slots = self._layout.equipment_slots
        if slot_index < 0 or slot_index >= len(slots):
            raise IndexError(f"装备槽索引 {slot_index} 超出范围 [0, {len(slots) - 1}]")
        return await self._capture_slot(slots[slot_index])

    async def capture_skill_slot(self, slot_index: int) -> ImageFrame:
        """悬停并截取指定技能槽位的 tooltip 图像。

        Args:
            slot_index: 技能槽索引，范围 0 ~ len(skill_slots)-1。
        """
        slots = self._layout.skill_slots
        if slot_index < 0 or slot_index >= len(slots):
            raise IndexError(f"技能槽索引 {slot_index} 超出范围 [0, {len(slots) - 1}]")
        return await self._capture_slot(slots[slot_index])

    async def capture_paragon_slot(self, slot_index: int) -> ImageFrame:
        """悬停并截取指定巅峰槽位的 tooltip 图像。

        Args:
            slot_index: 巅峰槽索引，范围 0 ~ len(paragon_slots)-1。
        """
        slots = self._layout.paragon_slots
        if slot_index < 0 or slot_index >= len(slots):
            raise IndexError(f"巅峰槽索引 {slot_index} 超出范围 [0, {len(slots) - 1}]")
        return await self._capture_slot(slots[slot_index])

    async def capture_amulet_slot(self, slot_index: int) -> ImageFrame:
        """悬停并截取指定护身符槽位的 tooltip 图像。

        Args:
            slot_index: 护身符槽索引，范围 0 ~ len(amulet_slots)-1。
        """
        slots = self._layout.amulet_slots
        if slot_index < 0 or slot_index >= len(slots):
            raise IndexError(
                f"护身符槽索引 {slot_index} 超出范围 [0, {len(slots) - 1}]"
            )
        return await self._capture_slot(slots[slot_index])

    # ------------------------------------------------------------------
    # 槽位数量查询（便于上层行为树循环）
    # ------------------------------------------------------------------

    @property
    def equipment_slot_count(self) -> int:
        """装备槽位数量。"""
        return len(self._layout.equipment_slots)

    @property
    def skill_slot_count(self) -> int:
        """技能槽位数量。"""
        return len(self._layout.skill_slots)

    @property
    def paragon_slot_count(self) -> int:
        """巅峰槽位数量。"""
        return len(self._layout.paragon_slots)

    @property
    def amulet_slot_count(self) -> int:
        """护身符槽位数量。"""
        return len(self._layout.amulet_slots)

    # ------------------------------------------------------------------
    # 槽位名称查询（便于上层构建输出文件名）
    # ------------------------------------------------------------------

    def equipment_slot_name(self, slot_index: int) -> str:
        return self._layout.equipment_slots[slot_index].name

    def skill_slot_name(self, slot_index: int) -> str:
        return self._layout.skill_slots[slot_index].name

    def paragon_slot_name(self, slot_index: int) -> str:
        return self._layout.paragon_slots[slot_index].name

    def amulet_slot_name(self, slot_index: int) -> str:
        return self._layout.amulet_slots[slot_index].name

    # ------------------------------------------------------------------
    # 关闭配置页
    # ------------------------------------------------------------------

    async def close(self) -> LeaderboardScreen:
        """点击右上角关闭按钮，等待返回天梯榜页面。

        Returns:
            就绪的 LeaderboardScreen 实例。
        """
        from d4_client.screens.leaderboard import LeaderboardScreen

        close_point = self._layout.close_btn
        logger.info("[PlayerConfigScreen] 关闭配置页 → %s", close_point)
        await self.window.mouse_click(point=close_point)

        screen = LeaderboardScreen(window=self.window)
        await screen.wait_until_visible()
        return screen
