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
            if status == NodeStatus.SUCCESS:
                return NodeStatus.SUCCESS
        return NodeStatus.FAILURE


@dataclass
class Sequence(BaseNode):
    children: list[BaseNode]

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        for child in self.children:
            status = await child.tick(blackboard)
            if status == NodeStatus.FAILURE:
                return NodeStatus.FAILURE
        return NodeStatus.SUCCESS
