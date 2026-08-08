"""梦幻西游 常驻主界面 (MainHUD) 页面对象模型。"""

import asyncio
from dataclasses import dataclass, field
import logging
from pathlib import Path
from typing import override

from cv_engine import abs_diff
from sys_input.models import MouseButton

from mhxy_client.config.main_hud import DB_CHANGAN_MAP
from mhxy_client.models.npcs.npc import Npc
from mhxy_client.screens.inventory import InventoryPanel
from mhxy_client.screens.panels.panels import Panels
from sys_input import VirtualKeyCode
from client_core import ImageFrame, OcrResult, RelativeRegion
from mhxy_client.models import SectTaskInfo
from mhxy_client.screens.base import BaseScreen
from mhxy_client.screens.dialogs.dialogs import Dialogs

logger = logging.getLogger(__name__)

# 未标定时的默认兜底选区
_DEFAULT_MAP_NAME_ROI = RelativeRegion(x=0.8, y=0.0, width=0.2, height=0.15)

# 已知的其他非师门任务标题 (用于分割师门任务多行描述文本)
_KNOWN_OTHER_TASKS = (
    "仙石天机",
    "雁塔试炼",
    "国子监拜师",
    "推荐",
    "帮派任务",
    "宝图任务",
    "日常任务",
    "师门寻路",
)

_DIALOG_BG_TEMPLATE_PATH = (
    Path(__file__).resolve().parents[3] / "templates" / "dialog_bg.png"
)

@dataclass
class MainHUD(BaseScreen):
    """梦幻西游 主界面常驻 HUD 视角与面板控制对象。"""

    screen_name: str = "MainHUD"
    dialogs: Dialogs = field(init=False)
    panels: Panels = field(init=False)
    inventory: InventoryPanel = field(init=False)
    
    sect_task_info: SectTaskInfo = field(init=False)
    
    _last_coordinate: ImageFrame | None = field(init=False, default=None)

    def __post_init__(self):
        self.dialogs = Dialogs(window=self.window)
        self.panels = Panels(window=self.window)
        self.inventory = InventoryPanel(window=self.window)
        self.sect_task_info = SectTaskInfo()
        self.is_visible: bool = True
        self._last_coordinate = None

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

    async def get_current_map(self) -> str | None:
        """获取当前所在的地图/场景名称 (如 '建邺城', '长安城')。

        根据配置的 map_name_roi 识别地图区域 OCR 文本，自动剥离坐标后缀。
        """
        roi =  self.config.map_name_roi
        result = await self.window.get_text(roi=roi)
        return result

    async def check_sect_task(self) -> SectTaskInfo:
        try:
            return await self._check_sect_task_by_task_list()
        except Exception as e:
            logger.exception("Failed to check sect task by task list", exc_info=e)
            return await self.check_sect_task_in_task_panel()

    async def check_sect_task_in_task_panel(self) -> SectTaskInfo:
        await self.open_task_panel()
        await asyncio.sleep(1)
        await self.window.begin_frame()
        task_info = await self._check_sect_task_one_line(
            roi=self.config.task_panel_roi_v2
        )
        await self.close_task_panel()
        return task_info

    async def open_task_panel(self) -> None:
        await self.window.hotkey([VirtualKeyCode.VK_MENU, VirtualKeyCode.VK_Q])
        
    async def close_task_panel(self) -> None:
        await self.window.hotkey([VirtualKeyCode.VK_MENU, VirtualKeyCode.VK_Q])
        
    async def _check_sect_task_by_task_list(self) -> SectTaskInfo:
        # roi =  self.config.task_list_roi
        # return await self._check_sect_task_by_roi(roi)
        return await self._check_sect_task_one_line(self.config.task_list_roi_v2)
        
    async def _check_sect_task_one_line(self, roi: RelativeRegion) -> SectTaskInfo:
        row_1 = await self.window.get_text(roi=roi)
        if not row_1:
            raise ValueError("No text found in the given ROI")
        row_2_roi = roi.move(0, roi.height)
        row_2 = await self.window.get_text(roi=row_2_roi)
        if not row_2:
            raise ValueError("No text found in the given ROI")
        full_description = row_1 + row_2
            
        row_1_rect = self.config.task_list_roi_v2.to_absolute(self.window.width, self.window.height)
        row_2_rect = row_1_rect.move(0, row_1_rect.height)
        task_info = SectTaskInfo(
            full_description=full_description,
            ocr_items=[OcrResult(
                text=row_1,
                confidence=1.0,
                rect=row_1_rect,
            ), OcrResult(
                text=row_2,
                confidence=1.0,
                rect=row_2_rect,
            )]
        )
        task_info.resolve()
        self.sect_task_info = task_info
        return task_info
        
    async def _check_sect_task_by_roi(self, roi: RelativeRegion) -> SectTaskInfo:
        results = await self.window.ocr(roi=roi)
        task_info = SectTaskInfo()
        if not results:
            return task_info

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
            raise ValueError("No sect task found in task list")

        sect_desc_ocr_items: list[OcrResult] = []
        for res in results[sect_title_idx + 1 :]:
            text = res.text.strip()
            if any(header in text for header in _KNOWN_OTHER_TASKS):
                break
            sect_desc_ocr_items.append(res)

        task_info.ocr_items = sect_desc_ocr_items
        task_info.resolve()

        self.sect_task_info = task_info

        return task_info

    async def do_sect_task(self):
        action_point = self.sect_task_info.action_point
        if action_point is None:
            raise ValueError("action_point is None")
        await self.mouse_click(action_point)
        
    async def confirm_give(self):
        await self.mouse_click(target_roi=self.config.confirm_give_roi)
        
    async def open_inventory(self):
        await self.inventory.open()
        
    async def open_map(self):
        await self.window.key_press(VirtualKeyCode.VK_TAB)

    async def close_map(self):
        await self.window.key_press(VirtualKeyCode.VK_TAB)
        
    async def lead_to_npc_house(self, target: Npc):
        await self.open_map()
        await self.mouse_click(target_roi=target.map_location)
        await self.close_map()
        
    async def return_shi_meng(self):
        await self.window.key_press(VirtualKeyCode.VK_F8)

    async def go_to_shi_fu(self):
        action_point = self.sect_task_info.resolve_point_by_targets(("师父", "父", "师"))
        await self.mouse_click(action_point)

    async def check_dialog_visible(self, npc_name: str="") -> bool:
        return not await self.window.abs_diff(
            roi=self.config.dialog_bg_roi,
            template_path=_DIALOG_BG_TEMPLATE_PATH
        )

    async def click_target_in_task_panel(self, target: str):
        targets = (target, *[i for i in target])
        action_point = self.sect_task_info.resolve_point_by_targets(targets)
        await self.mouse_click(action_point)
        
    async def choose_option_in_dialog(self, dialog_name: str, option: str, retry: bool=True):
        element = await self.locate_element(
            element_key=f"dialog:{dialog_name}:{option}",
            target_text=option,
            roi=self.config.dialog_roi,
            is_element_fixed=False,
        )
        if element is None and retry:
            await self.mouse_move(target_roi=self.config.dialog_roi)
            element = await self.locate_element(
                element_key=f"dialog:{dialog_name}:{option}",
                target_text=option,
                roi=self.config.dialog_roi,
                is_element_fixed=False,
            )
        if element is None:
            raise RuntimeError(f"未能定位到选项元素: {option} in dialog: {dialog_name}")
        await self.mouse_click(target_roi=element.region)

    async def go_to_shop(self, target: str):
        await self.open_map()
        roi = DB_CHANGAN_MAP.get(target)
        if roi is None:
            raise ValueError(f"未找到商店位置: {target}")
        await self.mouse_click(target_roi=roi)
        await asyncio.sleep(0.1)
        await self.close_map()

    async def interact_with_npc(self, npc_name: str):
        roi = DB_CHANGAN_MAP.get(npc_name)
        if roi is None:
            raise ValueError(f"未找到 NPC 位置: {npc_name}")
        await self.clean_players()
        await self.mouse_click(target_roi=roi)
        
    async def close_dialog(self) -> None:
        await self.click(
            target_roi=self.config.dialog_roi,
            button=MouseButton.RIGHT
        )

    async def clean_players(self) -> None:
        await self.window.key_press(VirtualKeyCode.VK_F9)

    async def is_moving(self) -> bool:
        current = await self.window.capture(self.config.coordinate_roi)
        if self._last_coordinate is None:
            self._last_coordinate = current
            return True
        result = abs_diff(
            current.mat,
            self._last_coordinate.mat,
        )
        self._last_coordinate = current
        return result