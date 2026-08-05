"""梦幻西游自动化黑板 (Blackboard) 聚合根。

Blackboard 是行为树各节点之间共享状态的载体，每帧 tick 时传递给根节点。
"""

from dataclasses import dataclass, field

from mhxy_client import MhxyClient
from mhxy_client.models import SectTaskInfo


@dataclass
class SectTaskContext:
    """师门任务跨帧状态上下文。

    存储上一帧检查到的任务状态，供条件节点读取，避免重复 OCR。
    """

    task_info: SectTaskInfo | None = None
    """最近一次 check_sect_task 的解析结果，None 表示尚未检查。"""

    go_to_shi_fu_triggered: bool = False
    """是否已发出过「前往师父」的点击指令，防止在寻路途中反复触发点击。"""



@dataclass
class Blackboard:
    """行为树黑板，持有 MhxyClient 与任务专用上下文。

    每帧开始前须先调用 client.begin_frame() 刷新画面缓存，
    再将本 Blackboard 传入行为树根节点的 tick()。
    """

    client: MhxyClient
    sect_task: SectTaskContext = field(default_factory=SectTaskContext)
