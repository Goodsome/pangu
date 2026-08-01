"""暗黑破坏神 4 天梯榜 (LeaderboardScreen) 页面对象模型。"""

from __future__ import annotations

import re
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, override

from d4_client.config.leaderboard import (
    LeaderboardLayoutConfig,
    load_leaderboard_config,
)
from d4_client.models import ImageFrame
from d4_client.screens.base import AutoCalibratingScreen

if TYPE_CHECKING:
    from d4_client.screens.player_config import PlayerConfigScreen  # type: ignore[reportImportCycles]

logger = logging.getLogger(__name__)

# 页码格式正则：匹配 "1/100"、"23 / 100" 等变体
_PAGE_PATTERN = re.compile(r"(\d+)\s*/\s*\d+")


@dataclass
class LeaderboardScreen(AutoCalibratingScreen):
    """暗黑破坏神 4 天梯榜页面对象。

    负责：
    - 职业切换
    - 整页记录区域截图
    - 逐行点击触发弹出菜单
    - 进入玩家配置页
    - 翻页
    """

    screen_name: str = "LeaderboardScreen"

    @property
    def _layout(self) -> LeaderboardLayoutConfig:
        return load_leaderboard_config().leaderboard

    # ------------------------------------------------------------------
    # 页面状态检测
    # ------------------------------------------------------------------

    @override
    async def is_visible(self) -> bool:
        """通过检测"天梯榜"标题文字判断当前是否处于天梯榜页面。"""
        result = await self.window.find_text(
            target_text=self._layout.title_text,
            roi=self._layout.title_roi,
        )
        return result is not None

    # ------------------------------------------------------------------
    # 职业选择
    # ------------------------------------------------------------------

    async def select_class(self, class_name: str) -> None:
        """点击顶部职业图标按钮切换榜单职业。

        Args:
            class_name: 职业名称，需与 leaderboard.yaml class_buttons 中的 key 一致。

        Raises:
            KeyError: 职业名不在配置中。
        """
        btn_point = self._layout.class_buttons[class_name]
        logger.info("[LeaderboardScreen] 切换职业 → %s (%s)", class_name, btn_point)
        await self.window.mouse_click(point=btn_point)

    # ------------------------------------------------------------------
    # 榜单区域截图
    # ------------------------------------------------------------------

    async def capture_records_region(self) -> ImageFrame:
        """截取当页 10 条记录所在矩形区域并返回图像帧。"""
        region = self._layout.records_region
        logger.debug("[LeaderboardScreen] 截取记录区域 %s", region)
        return await self.window.capture(region=region)

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
        points = self._layout.row_click_points
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

        cfg = self._layout.view_config_button
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
        point = self._layout.next_page_btn
        logger.info("[LeaderboardScreen] 翻到下一页 → %s", point)
        await self.window.mouse_click(point=point)

    async def current_page_number(self) -> int | None:
        """通过 OCR 识别页码区域，返回当前页码整数。

        识别目标格式："N/M"（如 "1/100"、"23/100"），提取分子 N。
        识别结果对多个 OCR 文本框逐一尝试，返回第一个匹配的页码。

        Returns:
            当前页码（从 1 开始），识别失败返回 None。
        """
        roi = self._layout.page_number_roi
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
        return self._layout.row_count
