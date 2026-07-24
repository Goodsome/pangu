from enum import StrEnum


class NodeStatus(StrEnum):
    SUCCESS = "success"
    FAILURE = "failure"
    RUNNING = "running"
    