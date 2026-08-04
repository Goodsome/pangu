"""师门任务相关数据模型。"""

from enum import StrEnum
from pydantic import BaseModel, Field
from client_core import Point


class SectTaskStatus(StrEnum):
    """师门任务当前状态枚举。"""

    NOT_FOUND = "not_found"  # 任务列表中未找到师门任务/未追踪
    CLAIMABLE = (
        "claimable"  # 可领取/需回师门 (如 "新的一天，回师门看看师父有什么吩咐吧")
    )
    IN_PROGRESS = "in_progress"  # 进行中 (寻路/送信/上交/巡逻等)


class SectTaskInfo(BaseModel):
    """师门任务解析结果与交互定位模型 (Pydantic 2.0 风格)。"""

    is_tracking_panel_open: bool = Field(
        default=False, description="任务追踪面板是否展开"
    )
    is_sect_task_active: bool = Field(
        default=False, description="师门任务是否在列表中处于追踪中"
    )
    status: SectTaskStatus = Field(
        default=SectTaskStatus.NOT_FOUND, description="师门任务当前状态"
    )
    task_title: str = Field(default="", description="任务标题 (如 '师门任务')")
    description_lines: list[str] = Field(
        default_factory=list, description="师门任务多行描述文本列表"
    )
    action_text: str = Field(
        default="", description="匹配到的可点击关键文本 (如 '父有什么吩咐吧。')"
    )
    action_point: Point | None = Field(
        default=None, description="自动寻路/交互的目标点物理坐标"
    )
