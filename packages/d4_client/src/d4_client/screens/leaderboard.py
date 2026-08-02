"""暗黑破坏神 4 天梯榜 (LeaderboardScreen) 页面对象模型。"""

from __future__ import annotations

import re
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, override

from d4_client.config.leaderboard import (
    LeaderboardLayoutConfig,
    LeaderboardLayoutConfigLegacy,
    load_leaderboard_config,
)
from d4_client.models import ImageFrame, Point
from d4_client.screens.base import AutoCalibratingScreen
from d4_types.enums.player_class import PlayerClass

if TYPE_CHECKING:
    from d4_client.screens.player_config import PlayerConfigScreen  # type: ignore[reportImportCycles]

logger = logging.getLogger(__name__)

# 页码格式正则：匹配 "1/100"、"23 / 100" 等变体
_PAGE_PATTERN = re.compile(r"(\d+)\s*/\s*\d+")


# 8 个职业在顶部 class_selector_roi 区域中从左到右的顺序 (8 等分)
ORDERED_PLAYER_CLASSES: tuple[PlayerClass, ...] = (
    PlayerClass.BARBARIAN,   # 1. 野蛮人
    PlayerClass.NECROMANCER, # 2. 死灵法师
    PlayerClass.SORCERER,    # 3. 巫师
    PlayerClass.ROGUE,       # 4. 游侠
    PlayerClass.DRUID,       # 5. 德鲁伊
    PlayerClass.SPIRITBORN,  # 6. 灵巫
    PlayerClass.PALADIN,     # 7. 圣骑士
    PlayerClass.WARLOCK,     # 8. 术士
)


@dataclass
class LeaderboardScreen(AutoCalibratingScreen):
    """暗黑破坏神 4 天梯榜页面对象。

    负责：
    - 职业切换 (使用新版 LeaderboardLayoutConfig 和 PlayerClass 枚举 8 等分区域计算)
    - 整页记录区域截图
    - 逐行点击触发弹出菜单
    - 进入玩家配置页
    - 翻页
    """

    screen_name: str = "LeaderboardScreen"

    @property
    def layout(self) -> LeaderboardLayoutConfig:
        """全新的天梯榜强类型相对物理布局配置。"""
        return LeaderboardLayoutConfig()

    @property
    def _legacy_layout(self) -> LeaderboardLayoutConfigLegacy:
        """旧版配置（渐进式替换过渡用）。"""
        return load_leaderboard_config().leaderboard

    # ------------------------------------------------------------------
    # 页面状态检测
    # ------------------------------------------------------------------

    @override
    async def is_visible(self) -> bool:
        """通过检测"天梯榜"标题文字判断当前是否处于天梯榜页面 (使用新版 layout)。"""
        result = await self.window.find_text(
            target_text=self.layout.title_text,
            roi=self.layout.title_roi,
        )
        return result is not None

    # ------------------------------------------------------------------
    # 职业选择
    # ------------------------------------------------------------------

    async def select_class(self, player_class: PlayerClass) -> Point:
        """点击顶部职业图标按钮切换榜单职业。

        通过 class_selector_roi (8等分区域) 结合 PlayerClass 枚举，计算得绝对点击像素点。

        Args:
            player_class: 职业枚举 (PlayerClass)。

        Returns:
            Point: 计算出的最终鼠标点击物理坐标。

        Raises:
            KeyError: 职业未包含在 8 等分选择器中。
        """
        if player_class not in ORDERED_PLAYER_CLASSES:
            raise KeyError(f"职业 '{player_class}' 未包含在 8 等分面板中")

        index = ORDERED_PLAYER_CLASSES.index(player_class)

        # 解算 0.0 ~ 1.0 的 class_selector_roi 到绝对像素 Region
        abs_roi = self.layout.class_selector_roi.to_absolute(
            window_width=self.window.width,
            window_height=self.window.height,
        )

        # 8 等分宽度计算中心点
        cell_width = abs_roi.width / len(ORDERED_PLAYER_CLASSES)
        center_x = int(round(abs_roi.x + cell_width * index + cell_width / 2.0))
        center_y = int(round(abs_roi.y + abs_roi.height / 2.0))
        btn_point = Point(x=center_x, y=center_y)

        await self.window.mouse_click(point=btn_point)
        return btn_point

    # ------------------------------------------------------------------
    # 榜单区域截图
    # ------------------------------------------------------------------

    async def capture_records_region(self, output_path: Path) -> Path:
        """截取当页 10 条记录所在矩形区域并保存为磁盘图片文件。

        使用新版 RelativeRegion records_roi 传入 window.capture 自动完成分辨率解算与截取。

        Args:
            output_path: 目标保存文件路径 (仅接受 Path 对象，必填)。

        Returns:
            Path: 保存后的图片绝对物理路径。
        """
        frame = await self.window.capture(region=self.layout.records_roi)
        await frame.save(output_path)
        logger.info("[LeaderboardScreen] 记录区域截图已保存 → %s", output_path)
        return output_path

    # ------------------------------------------------------------------
    # 行交互
    # ------------------------------------------------------------------

    async def click_row(self, row_index: int) -> None:
        """点击指定行，触发弹出上下文菜单。

        Args:
            row_index: 行索引，范围 0-9（对应榜单第 1-10 名）。

        Raises:
            IndexError: row_index 超出有效范围。
        """
        points = self._legacy_layout.row_click_points
        if row_index < 0 or row_index >= len(points):
            raise IndexError(f"row_index={row_index} 超出范围 [0, {len(points) - 1}]")
        point = points[row_index]
        logger.info("[LeaderboardScreen] 点击第 %d 行 → %s", row_index + 1, point)
        await self.window.mouse_click(point=point)

    # ------------------------------------------------------------------
    # 打开玩家配置页
    # ------------------------------------------------------------------

    async def open_player_config(self) -> PlayerConfigScreen:
        """定位弹出菜单中的"查看配置"按钮并点击，等待配置页加载完成。

        Returns:
            加载就绪的 PlayerConfigScreen 实例。

        Raises:
            RuntimeError: 无法定位"查看配置"按钮。
        """
        from d4_client.screens.player_config import PlayerConfigScreen

        cfg = self._legacy_layout.view_config_button
        clicked = False

        if cfg.strategy == "template" and cfg.template.exists():
            clicked = await self.window.match_and_click(template=cfg.template)
            if not clicked:
                logger.warning(
                    "[LeaderboardScreen] 模板匹配'查看配置'按钮失败，降级至文字识别"
                )

        if not clicked:
            # 降级：OCR 文字识别点击
            clicked = await self.window.find_text_and_click(
                target_text="查看配置",
                exact_match=True,
            )

        if not clicked:
            raise RuntimeError("[LeaderboardScreen] 无法定位'查看配置'按钮")

        screen = PlayerConfigScreen(window=self.window)
        await screen.wait_until_visible()
        return screen

    # ------------------------------------------------------------------
    # 翻页
    # ------------------------------------------------------------------

    async def next_page(self) -> None:
        """点击"下一页"按钮翻页。"""
        point = self._legacy_layout.next_page_btn
        logger.info("[LeaderboardScreen] 翻到下一页 → %s", point)
        await self.window.mouse_click(point=point)

    async def current_page_number(self) -> int | None:
        """通过 OCR 识别页码区域，返回当前页码整数。

        识别目标格式："N/M"（如 "1/100"、"23/100"），提取分子 N。
        识别结果对多个 OCR 文本框逐一尝试，返回第一个匹配的页码。

        Returns:
            当前页码（从 1 开始），识别失败返回 None。
        """
        roi = self._legacy_layout.page_number_roi
        results = await self.window.ocr(roi=roi)

        for ocr in results:
            m = _PAGE_PATTERN.search(ocr.text)
            if m:
                page = int(m.group(1))
                logger.debug(
                    "[LeaderboardScreen] 识别页码: %d（原文: %r）", page, ocr.text
                )
                return page

        logger.warning("[LeaderboardScreen] 页码 OCR 未识别到有效结果，区域=%s", roi)
        return None

    @property
    def row_count(self) -> int:
        """每页的固定行数（由配置决定，通常为 10）。"""
        return self._legacy_layout.row_count
