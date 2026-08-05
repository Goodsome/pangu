"""梦幻西游 常驻主界面 (MainHUD) 页面对象模型。"""

from dataclasses import dataclass, field
import logging
from typing import override

from mhxy_client.models.npcs.npc import Npc
from mhxy_client.screens.inventory import InventoryPanel
from sys_input import VirtualKeyCode
from client_core import OcrResult, RelativeRegion
from mhxy_client.models import SectTaskInfo
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
    inventory: InventoryPanel = field(init=False)

    def __post_init__(self):
        self.dialogs = Dialogs(window=self.window)
        self.inventory = InventoryPanel(window=self.window)
        self.is_visible: bool = True

    @override
    async def check_visible(self) -> bool:
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

        sect_desc_ocr_items: list[OcrResult] = []
        for res in results[sect_title_idx + 1 :]:
            text = res.text.strip()
            if any(header in text for header in _KNOWN_OTHER_TASKS):
                break
            sect_desc_ocr_items.append(res)

        task_info.ocr_items = sect_desc_ocr_items
        task_info.resolve()

        return task_info

    async def do_sect_task(self):
        task_info = await self.check_sect_task()
        action_point = task_info.action_point
        if action_point is None:
            raise ValueError("action_point is None")
        await self.mouse_click(action_point)
        
    async def confirm_give(self):
        await self.mouse_click(self.config.confirm_give_roi.center)
        
    async def open_inventory(self):
        await self.inventory.open()
        
    async def open_map(self):
        await self.window.key_press(VirtualKeyCode.VK_TAB)

    async def close_map(self):
        await self.window.key_press(VirtualKeyCode.VK_TAB)
        
    async def lead_to_npc_house(self, target: Npc):
        await self.open_map()
        await self.mouse_click(target.map_location.center)
        await self.close_map()
        