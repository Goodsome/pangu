from typing import override

from mhxy_client.screens.base import BaseScreen
from sys_input.models import MouseButton


class HuiBeiDialog(BaseScreen):

    @override
    async def is_visible(self) -> bool:
        element = await self.locate_element(
            element_key="dialog_name",
            target_text="慧悲",
            roi=self.config.dialog_name_roi
        )
        return element is not None

    async def do_sect_task(self) -> None:
        element = await self.locate_element(
            element_key="sect_task",
            target_text="师门任务",
            roi=self.config.dialog_roi,
            is_element_fixed=True,
        )
        if element is None:
            raise RuntimeError("未能定位到师门任务元素")
        await self.mouse_click(element.region.center)

    async def close_dialog(self) -> None:
        await self.window.mouse_click(button=MouseButton.RIGHT)
