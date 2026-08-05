"""行为树节点状态枚举。"""

from enum import StrEnum


class NodeStatus(StrEnum):
    SUCCESS = "success"
    FAILURE = "failure"
    RUNNING = "running"
