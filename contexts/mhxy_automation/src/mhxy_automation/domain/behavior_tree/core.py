"""行为树核心原语：节点基类与组合节点。

单帧执行契约
-----------
每次 tick() 调用只处理**当前帧**已捕获的画面数据，不得在内部执行
跨帧等待（禁止 await asyncio.sleep / 循环轮询）。

- SUCCESS  : 本帧节点目标已达成
- FAILURE  : 本帧节点目标未能达成（或前置条件不满足）
- RUNNING  : 本帧已发起一个动作或完成一次检查，需要下帧继续确认
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.enums.node_status import NodeStatus


class BaseNode(ABC):
    """行为树节点抽象基类。"""

    @abstractmethod
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        """执行本节点逻辑，返回当前帧的执行状态。"""
        ...


@dataclass
class Selector(BaseNode):
    """选择节点（OR 语义）。

    从左到右依次 tick 子节点：
    - 子节点返回 SUCCESS 或 RUNNING → 立即返回该状态，不再 tick 后续节点
    - 子节点返回 FAILURE → 继续 tick 下一个子节点
    - 所有子节点均 FAILURE → 返回 FAILURE
    """

    children: list[BaseNode]

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        for child in self.children:
            status = await child.tick(blackboard)
            if status != NodeStatus.FAILURE:
                return status
        return NodeStatus.FAILURE


@dataclass
class Sequence(BaseNode):
    """顺序节点（AND 语义）。

    从左到右依次 tick 子节点：
    - 子节点返回 FAILURE 或 RUNNING → 立即返回该状态，不再 tick 后续节点
    - 子节点返回 SUCCESS → 继续 tick 下一个子节点
    - 所有子节点均 SUCCESS → 返回 SUCCESS
    """

    children: list[BaseNode]

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        for child in self.children:
            status = await child.tick(blackboard)
            if status != NodeStatus.SUCCESS:
                return status
        return NodeStatus.SUCCESS
