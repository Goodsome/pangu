"""梦幻西游 常驻主界面 (MainHUD) 页面对象模型。"""

import asyncio
from dataclasses import dataclass, field
import logging
from typing import Literal, override

from pathlib import Path

from client_core import AutoCalibratingScreen, OcrResult, Point, Region, RelativeRegion
from mhxy_client.config import MainHudLayoutConfig
from mhxy_client.models import SectTaskInfo, SectTaskStatus
from mhxy_client.screens.inventory import InventoryPanel
from mhxy_client.screens.social import SocialPanel
from sys_input import VirtualKeyCode

logger = logging.getLogger(__name__)

_DEFAULT_CURSOR_TEMPLATE_PATH = Path(__file__).resolve().parents[3] / "templates" / "cursor.png"
_DEFAULT_POINTER_TEMPLATE_PATH = Path(__file__).resolve().parents[3] / "templates" / "pointer.png"

# 未标定时的默认兜底选区
_DEFAULT_MAP_NAME_ROI = RelativeRegion(x=0.8, y=0.0, width=0.2, height=0.15)
_DEFAULT_TASK_LIST_ROI = RelativeRegion(x=0.75, y=0.15, width=0.25, height=0.5)

# 已知的其他非师门任务标题 (用于分割师门任务多行描述文本)
_KNOWN_OTHER_TASKS = (
    "仙石天机",
    "雁塔试炼",
    "国子监拜师",
    "推荐",
    "帮派任务",
    "宝图任务",
    "日常任务",
)


def calculate_substring_point(
    text: str,
    target_sub: str,
    rect: Region,
) -> Point | None:
    """在单行 OCR 识别文本框中，基于字符分布横向比例精准计算特定子字符串 (如 '师父'/'父'/'师') 的像素中心点。

    Args:
        text: OCR 识别出的完整行文本
        target_sub: 要定位的子字符串 (如 "师父", "父", "师")
        rect: 完整行文本的像素矩形 Region

    Returns:
        Point | None: 该子字符串的中心像素坐标 Point；若未找到子串则返回 None
    """
    if not text or not target_sub or target_sub not in text:
        return None

    n = len(text)
    if n == 0:
        return None

    start_idx = text.find(target_sub)
    end_idx = start_idx + len(target_sub)

    # 算得子字符串在整行字符宽度上的相对比例中心 (0.0 ~ 1.0)
    center_ratio = (start_idx + end_idx) / (2.0 * n)

    center_x = int(rect.x + rect.width * center_ratio)
    center_y = int(rect.y + rect.height / 2.0)

    return Point(x=center_x, y=center_y)


@dataclass
class MainHUD(AutoCalibratingScreen):
    """梦幻西游 主界面常驻 HUD 视角与面板控制对象。"""

    screen_name: str = "MainHUD"
    layout: MainHudLayoutConfig = field(default_factory=MainHudLayoutConfig)

    @override
    async def is_visible(self) -> bool:
        """检查当前界面是否为主 HUD 视角。"""
        roi = (
            self.layout.map_name_roi
            if self.layout.map_name_roi.width > 0
            and self.layout.map_name_roi.height > 0
            else _DEFAULT_MAP_NAME_ROI
        )
        results = await self.window.ocr(roi=roi)
        for result in results:
            if result.text:
                return True
        return False

    async def get_current_map(self) -> str:
        """获取当前所在的地图/场景名称 (如 '建邺城', '长安城')。

        根据配置的 map_name_roi 识别地图区域 OCR 文本，自动剥离坐标后缀。
        """
        roi = (
            self.layout.map_name_roi
            if self.layout.map_name_roi.width > 0
            and self.layout.map_name_roi.height > 0
            else _DEFAULT_MAP_NAME_ROI
        )
        results = await self.window.ocr(roi=roi)
        for result in results:
            text = result.text.strip()
            if not text:
                continue
            # 过滤并清洗末尾坐标，例如 "建邺城 [105, 42]" / "建邺城 (105, 42)" -> "建邺城"
            clean_map = text.split("[")[0].split("(")[0].strip()
            if clean_map:
                return clean_map
        return ""

    async def check_sect_task(self) -> SectTaskInfo:
        """检查并解析主界面任务列表区域中的师门任务 (Sect Task)。

        解析任务追踪面板是否展开、师门任务是否处于追踪中，
        提取师门任务多行描述文本，判定任务状态 (如可领取 CLAIMABLE / 进行中 IN_PROGRESS)，
        并精确定位包含 '师父'/'父'/'师' 等可交互超链接文字的精准像素坐标 Point。
        """
        roi = (
            self.layout.task_list_roi
            if self.layout.task_list_roi.width > 0
            and self.layout.task_list_roi.height > 0
            else _DEFAULT_TASK_LIST_ROI
        )
        results = await self.window.ocr(roi=roi)
        logger.info(
            "[%s] 开始扫描任务列表区域 (ROI: %s)，共检索到 %d 条 OCR 文本",
            self.screen_name,
            roi,
            len(results),
        )

        task_info = SectTaskInfo()
        if not results:
            return task_info

        # 1. 检查任务追踪面板是否开启 (画面中包含 "任务追踪")
        for res in results:
            if "任务追踪" in res.text:
                task_info.is_tracking_panel_open = True
                break

        # 2. 定位 "师门任务" 标题位置
        sect_title_idx = -1
        for idx, res in enumerate(results):
            if "师门任务" in res.text:
                sect_title_idx = idx
                task_info.is_sect_task_active = True
                task_info.task_title = res.text.strip()
                break

        if sect_title_idx == -1:
            logger.info(
                "[%s] 任务列表中未检测到 '师门任务' 处于追踪状态", self.screen_name
            )
            return task_info

        # 3. 从 "师门任务" 下一行开始遍历解析多行描述文本，遇到下一个任务标题则截止
        sect_desc_ocr_items: list[OcrResult] = []
        for res in results[sect_title_idx + 1 :]:
            text = res.text.strip()
            # 若遇到其他已知任务标题，代表当前师门任务描述结束
            if any(header in text for header in _KNOWN_OTHER_TASKS):
                break
            sect_desc_ocr_items.append(res)

        task_info.description_lines = [item.text for item in sect_desc_ocr_items]
        full_desc = "".join(task_info.description_lines)

        logger.info(
            "[%s] 识别到师门任务描述 (%d 行): %s",
            self.screen_name,
            len(task_info.description_lines),
            full_desc,
        )

        # 4. 判定师门任务状态 (如可领取 CLAIMABLE / 进行中 IN_PROGRESS)
        claimable_keywords = ("回师门", "师父有什么吩咐", "领取", "新的一天", "吩咐")
        if any(kw in full_desc for kw in claimable_keywords):
            task_info.status = SectTaskStatus.CLAIMABLE
        else:
            task_info.status = SectTaskStatus.IN_PROGRESS

        # 5. 精确计算可点击超链接文字 ('师父' / '父' / '师') 的物理中心坐标
        # 优先级: 1) 完整 "师父"  2) 换行开头的 "父"  3) 换行末尾的 "师"
        search_targets = ("师父", "父", "师")

        for target in search_targets:
            for item in sect_desc_ocr_items:
                if target in item.text:
                    sub_point = calculate_substring_point(
                        text=item.text, target_sub=target, rect=item.rect
                    )
                    if sub_point is not None:
                        task_info.action_text = target
                        task_info.action_point = sub_point
                        logger.info(
                            "[%s] 🎯 精确定位到可点击超链接文字 '%s' (整行: '%s') -> 物理坐标: %s",
                            self.screen_name,
                            target,
                            item.text,
                            sub_point,
                        )
                        break
            if task_info.action_point is not None:
                break

        return task_info

    async def _get_cursor_region(self) -> Region:
        sys_client_pos = await self.window.ensure_cursor_in_window()
        radius = 50
        win_w = self.window.width
        win_h = self.window.height

        roi_x = max(0, sys_client_pos.x - radius)
        roi_y = max(0, sys_client_pos.y - radius)
        roi_w = min(win_w - roi_x, radius * 2)
        roi_h = min(win_h - roi_y, radius * 2)
        return Region(x=roi_x, y=roi_y, width=roi_w, height=roi_h)

    async def _get_game_mouse(self) -> tuple[Point | None, bool]:
        """获取游戏鼠标指针位置。"""

        roi = await self._get_cursor_region()
        await self.window.begin_frame()
        pointer_result = await self.window.match_template_masked(
            template=_DEFAULT_POINTER_TEMPLATE_PATH,
            threshold=0.7,
            roi=roi,
        )
        cursor_result = await self.window.match_template_masked(
            template=_DEFAULT_CURSOR_TEMPLATE_PATH,
            threshold=0.7,
            roi=roi,
        )
        if pointer_result is not None and cursor_result is not None:
            if pointer_result.score > cursor_result.score:
                return pointer_result.top_left, True
            return cursor_result.top_left, False
        elif pointer_result is None and cursor_result is not None:
            return cursor_result.top_left, False
        elif pointer_result is not None and cursor_result is None:
            return pointer_result.top_left, True
        else:
            return None, False

    async def _calibrate_and_realign_mouse(
        self,
        target_point: Point,
        tolerance_px: float = 10.0,
    ) -> bool:
        """单次测量游戏鼠标与目标的误差，按偏移量反算绝对像素坐标并移动矫正。

        Returns:
            tuple[Point, float]: (当前游戏鼠标实际位置, 距离目标的像素残差距离)
        """
        sys_client_pos = await self.window.ensure_cursor_in_window()
        game_cursor, is_pointer = await self._get_game_mouse()
        if game_cursor is None:
            raise RuntimeError("未匹配到游戏鼠标模板 cursor.png")
        if is_pointer:
            return True
        offset_x = game_cursor.x - sys_client_pos.x
        offset_y = game_cursor.y - sys_client_pos.y

        dx = float(game_cursor.x - target_point.x)
        dy = float(game_cursor.y - target_point.y)
        dist: float = (dx * dx + dy * dy) ** 0.5

        if dist <= tolerance_px:
            return True

        corrected_target = Point(
            x=target_point.x - offset_x,
            y=target_point.y - offset_y,
        )
        await self.window.smooth_mouse_move(point=corrected_target)
        await asyncio.sleep(0.1)
        return False

    async def _move_and_align_cursor_to_target(
        self,
        target_point: Point,
        max_retries: int = 5,
        tolerance_px: float = 10.0,
    ) -> bool:
        """循环调用 _calibrate_and_realign_mouse，直至实际游戏鼠标与目标点差距在 tolerance_px (10px) 以内。"""
        _ = await self.window.ensure_cursor_in_window()

        for attempt in range(1, max_retries + 1):
            result = await self._calibrate_and_realign_mouse(
                target_point=target_point,
                tolerance_px=tolerance_px,
            )
            if result:
                return True

        logger.warning( "达到最大校准重试次数")
        return False

    async def claim_sect_task(
        self,
        move_only: bool = False,
        delay_before_click_sec: float = 1.0,
    ) -> bool:
        """检查并触发师门任务领取/寻路交互。

        Args:
            move_only: 若为 True，仅将鼠标光标移动至目标位置，不执行点击 (用于调试校准)
            smooth_move: 若为 True，开启鼠标缓慢/平滑划动轨迹移动，避免瞬移引发跳变下漂 (默认 True)
            delay_before_click_sec: 光标移动到位后、执行点击前的等待延时秒数 (默认 1.0s)
            smooth_duration_sec: 平滑移动的总耗时秒数 (默认 1.0s)

        Returns:
            bool: 成功触发移动/点击返回 True，否则返回 False
        """
        task_info = await self.check_sect_task()
        if (
            task_info.status != SectTaskStatus.CLAIMABLE
            or task_info.action_point is None
        ):
            logger.warning(
                "[%s] 无法触发师门任务领取 (当前状态: %s, 坐标: %s)",
                self.screen_name,
                task_info.status,
                task_info.action_point,
            )
            return False

        target_point = task_info.action_point
        logger.info(
            "[%s] 🎯 定位到师门任务超链接文字 '%s'，目标相对坐标 %s",
            self.screen_name,
            task_info.action_text,
            target_point,
        )

        # 循环调用校准移动，直到与目标点差距在 10px 以内
        _ = await self._move_and_align_cursor_to_target(
            target_point=target_point,
            max_retries=5,
            tolerance_px=10.0,
        )

        if move_only:
            logger.info(
                "[%s] [Move Only 模式] 鼠标指针已精准停靠，跳过点击操作",
                self.screen_name,
            )
            return True

        # 悬停沉淀等待
        if delay_before_click_sec > 0:
            logger.info(
                "[%s] ⏳ 暂停等待 %.2f 秒以稳定鼠标焦点...",
                self.screen_name,
                delay_before_click_sec,
            )
            await asyncio.sleep(delay_before_click_sec)

        # 发送物理鼠标点击事件
        logger.info("[%s] 🚀 正在触发原点物理点击...", self.screen_name)
        await self.window.mouse_click(point=None)
        logger.info("[%s] ✅ 原点物理点击完成！", self.screen_name)
        return True

    async def open_inventory(self) -> InventoryPanel:
        """按下快捷键打开道具/背包面板并返回 InventoryPanel 实例。"""
        await self.window.key_press(VirtualKeyCode.VK_E)
        screen = InventoryPanel(window=self.window)
        await screen.wait_until_visible()
        return screen

    async def open_social(self) -> SocialPanel:
        """按下快捷键打开社交面板并返回 SocialPanel 实例。"""
        await self.window.key_press(VirtualKeyCode.VK_F)
        screen = SocialPanel(window=self.window)
        await screen.wait_until_visible()
        return screen
