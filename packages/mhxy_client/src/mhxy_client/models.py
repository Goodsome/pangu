"""mhxy_client 领域数据模型与梦幻西游标题解析。"""

from enum import StrEnum
import re

from pydantic import BaseModel, Field

from client_core import (
    BaseRegion,
    Element,
    ImageFrame,
    MatchResult,
    OcrResult,
    Point,
    Region,
    RelativePoint,
    RelativeRegion,
    SplitMode,
    WindowRectInfo as BaseWindowRectInfo,
)

# 梦幻西游客户端真实窗口标题正则解析: 梦幻西游 ONLINE - (畅玩服[天下无双] - 游易幽寒[39200278])
MHXY_TITLE_PATTERN = re.compile(
    r"梦幻西游\s*ONLINE\s*-\s*\((?P<server>.+?)\s*-\s*(?P<role_name>.+?)\[(?P<role_id>\d+)\]\)",
    re.IGNORECASE,
)


class WindowRectInfo(BaseWindowRectInfo):
    """扩展梦幻西游标题解析特性的 WindowRectInfo。"""

    @property
    def server_name(self) -> str:
        """从窗口标题中提取的服务器/大区名称 (如 '畅玩服[天下无双]')。"""
        m = MHXY_TITLE_PATTERN.search(self.title)
        return m.group("server").strip() if m else ""

    @property
    def role_name(self) -> str:
        """从窗口标题中提取的角色名字 (如 '游易幽寒')。"""
        m = MHXY_TITLE_PATTERN.search(self.title)
        return m.group("role_name").strip() if m else ""

    @property
    def role_id(self) -> str:
        """从窗口标题中提取的角色数字 ID (如 '39200278')。"""
        m = MHXY_TITLE_PATTERN.search(self.title)
        return m.group("role_id").strip() if m else ""


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


__all__ = [
    "BaseRegion",
    "Element",
    "ImageFrame",
    "MHXY_TITLE_PATTERN",
    "MatchResult",
    "OcrResult",
    "Point",
    "Region",
    "RelativePoint",
    "RelativeRegion",
    "SectTaskInfo",
    "SectTaskStatus",
    "SplitMode",
    "WindowRectInfo",
]
