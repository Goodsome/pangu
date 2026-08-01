from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import override

from d4_automation.domain.aggregates.blackboard import Blackboard
from d4_automation.domain.enums.node_status import NodeStatus


class BaseNode(ABC):
    @abstractmethod
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        pass


@dataclass
class Selector(BaseNode):
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
    children: list[BaseNode]

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        for child in self.children:
            status = await child.tick(blackboard)
            if status != NodeStatus.SUCCESS:
                return status
        return NodeStatus.SUCCESS


@dataclass
class RepeatUntilFail(BaseNode):
    """装饰器节点：持续 tick 子节点直到子节点返回 FAILURE。

    子节点返回 SUCCESS 或 RUNNING → 继续循环。
    子节点返回 FAILURE → 停止循环，本节点返回 SUCCESS。
    """

    child: BaseNode

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        while True:
            status = await self.child.tick(blackboard)
            if status == NodeStatus.FAILURE:
                return NodeStatus.SUCCESS
