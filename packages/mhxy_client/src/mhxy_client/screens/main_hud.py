"""梦幻西游 常驻主界面 (MainHUD) 页面对象模型。"""

import asyncio
from dataclasses import dataclass, field
import logging
from typing import override

from client_core import OcrResult, RelativeRegion
from mhxy_client.models import SectTaskInfo, SectTaskStatus
from mhxy_client.screens.base import BaseScreen
from mhxy_client.screens.dialogs.dialogs import Dialogs

logger = logging.getLogger(__name__)

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


@dataclass
class MainHUD(BaseScreen):
    """梦幻西游 主界面常驻 HUD 视角与面板控制对象。"""

    screen_name: str = "MainHUD"
    dialogs: Dialogs = field(init=False)

    def __post_init__(self):
        self.dialogs = Dialogs(window=self.window)

    @override
    async def is_visible(self) -> bool:
        """检查当前界面是否为主 HUD 视角。"""
        roi = (
            self.config.map_name_roi
            if self.config.map_name_roi.width > 0
            and self.config.map_name_roi.height > 0
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
            self.config.map_name_roi
            if self.config.map_name_roi.width > 0
            and self.config.map_name_roi.height > 0
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
        roi =  self.config.task_list_roi
        results = await self.window.ocr(roi=roi)
        task_info = SectTaskInfo()
        if not results:
            return task_info

        for res in results:
            if "任务追踪" in res.text:
                task_info.is_tracking_panel_open = True
                break

        sect_title_idx = -1
        for idx, res in enumerate(results):
            if "师门任务" in res.text:
                sect_title_idx = idx
                task_info.is_sect_task_active = True
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

        task_info.ocr_items = sect_desc_ocr_items
        task_info.resolve()

        return task_info


    async def claim_sect_task(
        self,
        delay_before_click_sec: float = 1.0,
    ) -> bool:
        """检查并触发师门任务领取/寻路交互。

        Args:
            move_only: 若为 True，仅将鼠标光标移动至目标位置，不执行点击 (用于调试校准)
            delay_before_click_sec: 光标移动到位后、执行点击前的等待延时秒数 (默认 1.0s)

        Returns:
            bool: 成功触发移动/点击返回 True，否则返回 False
        """
        task_info = await self.check_sect_task()
        if (
            task_info.status != SectTaskStatus.CLAIMABLE
            or task_info.action_point is None
        ):
            logger.warning( "[%s] 无法触发师门任务领取 (当前状态: %s, 坐标: %s)",
                self.screen_name,
                task_info.status,
                task_info.action_point,
            )
            return False

        target_point = task_info.action_point

        await self.mouse_move(target_point=target_point)

        if delay_before_click_sec > 0:
            logger.info(
                "[%s] ⏳ 暂停等待 %.2f 秒以稳定鼠标焦点...",
                self.screen_name,
                delay_before_click_sec,
            )
            await asyncio.sleep(delay_before_click_sec)

        await self.window.mouse_click(point=None)
        return True

    async def do_sect_task(self):
        task_info = await self.check_sect_task()
        action_point = task_info.action_point
        if action_point is None:
            raise ValueError("action_point is None")
        await self.mouse_click(action_point)
        
    async def confirm_give(self):
        await self.mouse_click(self.config.confirm_give_roi.center)
        