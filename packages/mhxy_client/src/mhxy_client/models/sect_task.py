"""师门任务相关数据模型。"""

import re
from dataclasses import dataclass, field
from enum import StrEnum, auto

from client_core import OcrResult, Point
from mhxy_client.models.task import calculate_substring_point


class SectTaskStatus(StrEnum):
    """师门任务当前状态枚举。"""

    NOT_FOUND = "not_found"
    CLAIMABLE = "claimable"
    IN_PROGRESS = "in_progress"
    REPORT = "report"


class TaskType(StrEnum):
    """任务类型枚举。"""

    SEND_MAIL = auto()
    SHOPPING = auto()
    PATROL = auto()


@dataclass
class SectTaskInfo:
    """师门任务解析结果与交互定位模型。"""

    is_tracking_panel_open: bool = False
    is_sect_task_active: bool = False
    status: SectTaskStatus = SectTaskStatus.NOT_FOUND
    description_lines: list[str] = field(default_factory=list)
    action_text: str = ""
    action_point: Point | None = None
    ocr_items: list[OcrResult] = field(default_factory=list)
    full_description: str = ""
    task_type: TaskType | None = None
    _task_target: str | None = None
    task_round: int | None = None
    has_item: bool = False

    @property
    def task_target(self) -> str:
        if self._task_target is None:
            raise ValueError("task_target is not resolved")
        return self._task_target

    def resolve(
        self,
    ) -> None:
        """从 OCR 文本项列表中按优先级精准查找可点击超链接文字并更新 action_text 和 action_point。"""

        self._resolve_full_description()
        self._resolve_status()
        self._resolve_action_point()

    def _resolve_full_description(self) -> None:
        """解析完整的师门任务描述文本。"""
        if self.full_description:
            return
        self.full_description = "".join(i.text for i in self.ocr_items)

    def _resolve_status(self) -> None:
        """解析任务状态。"""
        if self.full_description.startswith("新的一天"):
            self.status = SectTaskStatus.CLAIMABLE
            self._task_target = "父"
        elif self.full_description.startswith("继续回师门"):
            self.status = SectTaskStatus.CLAIMABLE
            self._task_target = "师父"
        elif match := re.search(
            r"帮师父送信给(.+?)，当", self.full_description
        ):
            self.status = SectTaskStatus.IN_PROGRESS
            self.task_type = TaskType.SEND_MAIL
            self._task_target = match.group(1)
        elif match := re.search(
            r"买到(.+?)送给师", self.full_description
        ):
            self.task_type = TaskType.SHOPPING
            if "已拥有" in self.full_description:
                self.has_item = True
                self.status = SectTaskStatus.REPORT
                self._task_target = "师父"
            else:
                self.status = SectTaskStatus.IN_PROGRESS
                self._task_target = match.group(1)
        elif match := re.search(
            r"在师门附近(.+?)当前", self.full_description
        ):
            self.status = SectTaskStatus.IN_PROGRESS
            self.task_type = TaskType.PATROL
            self._task_target = match.group(1)
            
        elif match := re.match(
            r"任务完成，找师父报告去", self.full_description
        ):
            self.status = SectTaskStatus.REPORT
            self._task_target = "师父"
        else:
            raise ValueError(f"Unresolved {self.full_description=}")

    def _resolve_action_point(self) -> None:
        """解析可点击超链接文字的物理中心坐标。"""
        match self.status:
            case SectTaskStatus.CLAIMABLE:
                self.action_point = self.resolve_point_by_targets(
                    search_targets=("师父", "父", "师"),
                )
            case SectTaskStatus.IN_PROGRESS:
                self.action_point = self._resove_in_progress_point()
            case SectTaskStatus.REPORT:
                self.action_point = self.resolve_point_by_targets(
                    search_targets=("师父",)
                )
            case _:
                raise NotImplementedError

    def resolve_point_by_targets(
        self,
        search_targets: tuple[str, ...],
        get_next_word: bool = False,
    ) -> Point:
        for target in search_targets:
            for item in self.ocr_items:
                if target in item.text:
                    sub_point = calculate_substring_point(
                        text=item.text,
                        target_sub=target,
                        rect=item.rect,
                        get_next_word=get_next_word,
                    )
                    if sub_point is not None:
                        return sub_point
        raise ValueError(f"Unknown claim task point: {self.full_description}")

    def _resove_in_progress_point(self) -> Point:
        assert self._task_target is not None
        return self.resolve_point_by_targets(
            search_targets=(self._task_target,),
        )