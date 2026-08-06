"""师门任务通用保障节点 (Ensure)。"""

from mhxy_automation.domain.behavior_tree.actions.sect_task import CloseDialog
from mhxy_automation.domain.behavior_tree.actions.sect_task.click_target_in_task_panel import (
    ClickTargetInTaskPanel,
)
from mhxy_automation.domain.behavior_tree.actions.sect_task.return_shi_meng import (
    ReturnShiMeng,
)
from mhxy_automation.domain.behavior_tree.conditions.sect_task.is_current_map import (
    IsInMap,
)
from mhxy_automation.domain.behavior_tree.conditions.sect_task.is_dialog_visible import (
    IsDialogVisible,
)
from mhxy_automation.domain.behavior_tree.core import Ensure, Not

ensure_in_shi_meng = Ensure(
    condition=IsInMap(["五庄观", "乾坤殿"]),
    action=ReturnShiMeng(),
)

ensure_shifu_dialog = Ensure(
    condition=IsDialogVisible("镇元大仙"),
    action=ClickTargetInTaskPanel(),
)

ensure_close_dialog = Ensure(
    condition=Not(IsDialogVisible()),
    action=CloseDialog(),
)
