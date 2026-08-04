    
from typing import override

from mhxy_client.screens.base import BaseScreen


class GuanYinJieJie(BaseScreen):

    @override
    async def is_visible(self) -> bool:
        element = await self.locate_element(
            element_key="dialog_name",
            target_text="观音姐姐",
            roi=self.layout.dialog_name_roi
        )
        return element is not None