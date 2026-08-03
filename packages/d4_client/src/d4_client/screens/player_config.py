"""暗黑破坏神 4 玩家配置查看器 (PlayerConfigScreen) 页面对象模型。"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, override

from d4_client.config.leaderboard import (
    LeaderboardLayoutConfig,
    PlayerConfigLayoutConfig,
    SlotConfig,
    load_leaderboard_config,
)
from client_core import AutoCalibratingScreen, ImageFrame, Region, RelativeRegion
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
    - 鼠标悬停各类槽位（装备/技能/巅峰/护身符）
    - 截取左侧 tooltip 预览区图像
    - 关闭配置页回到天梯榜
    """

    player_class: PlayerClass
    page: int
    row: int
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

    # ------------------------------------------------------------------
    # 各类槽位公开截图接口
    # ------------------------------------------------------------------

    async def capture_equipment_slot(
        self,
        output_dir: Path,
        slot_index: int,
    ) -> Path:
        """悬停并截取指定装备槽位的 tooltip 图像，并使用持有的状态保存到指定目录。

        Args:
            output_dir: 保存图片的目录路径 (Path)。
            slot_index: 装备槽索引 (0 ~ 8+second_row_count-1)。

        Returns:
            Path: 保存的图片绝对物理/相对路径。

        Raises:
            IndexError: 当 slot_index 超出有效范围时抛出。
        """
        slot_roi = self.get_equipment_slot_roi(slot_index)

        await self.window.mouse_click(
            point=slot_roi.center
        )
        await asyncio.sleep(0.5)

        tooltip_roi = self.get_equipment_tooltip_roi(slot_roi)
        logger.debug(
            "[PlayerConfigScreen] 悬停装备槽位 index=%d, 装备ROI=%s, tooltip ROI=%s",
            slot_index,
            slot_roi,
            tooltip_roi,
        )
        frame = await self.window.capture(region=tooltip_roi, refresh=True)

        class_str = self.player_class.value
        file_name = f"{class_str}_{self.page}_{self.row}_{slot_index}.png"
        save_path = output_dir / file_name

        await frame.save(save_path)
        logger.info(
            "[PlayerConfigScreen] 装备槽位 [%d] 截图已保存 → %s", slot_index, save_path
        )
        return save_path

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
