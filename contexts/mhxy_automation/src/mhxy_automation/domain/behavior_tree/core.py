"""行为树核心原语：节点基类与组合节点。

单帧执行契约
-----------
每次 tick() 调用只处理**当前帧**已捕获的画面数据，不得在内部执行
跨帧等待（禁止 await asyncio.sleep / 循环轮询）。

- SUCCESS  : 本帧节点目标已达成
- FAILURE  : 本帧节点目标未能达成（或前置条件不满足）
- RUNNING  : 本帧已发起一个动作或完成一次检查，需要下帧继续确认

生命周期钩子
-----------
reset() 由父节点在以下时机调用：
- 某个高优先级子节点成功，导致当前 RUNNING 子节点被"短路/中断"
- 父节点自身被上层节点 reset()，需要递归清理

节点应在 reset() 中恢复自身内部状态，使其可以被重新 tick()。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import override

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.enums.node_status import NodeStatus


class BaseNode(ABC):
    """行为树节点抽象基类。"""

    @abstractmethod
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        """执行本节点逻辑，返回当前帧的执行状态。"""
        ...

    def reset(self) -> None:
        """框架生命周期钩子：重置节点内部状态。

        当节点被父节点中断（例如 Selector 中更高优先级的条件节点成功）
        或整个树分支被重置时，由父节点调用此方法。
        默认实现为空操作；有内部状态的节点应覆写此方法。
        """
        pass

@dataclass
class Condition(BaseNode, ABC):
    """条件节点。"""
    

@dataclass
class Action(BaseNode, ABC):
    """动作节点。"""

@dataclass
class Composite(BaseNode, ABC):
    """复合节点基类。"""
    children: list[BaseNode]
    _running_child: BaseNode | None = field(default=None, init=False, repr=False)

    def set_running_child(self, node: BaseNode) -> None:
        """当节点返回 RUNNING 时调用：
        
        若发生优先级抢占（新的 running 节点不同于旧的），则中断重置旧节点。
        """
        if self._running_child is not None and self._running_child is not node:
            self._running_child.reset()
        self._running_child = node

    def clear_running_child(self, current_node: BaseNode | None = None) -> None:
        """当节点返回 SUCCESS 或 FAILURE 时调用：
        
        传入 current_node，用于豁免该节点（因为它自然结束了，不需要被中断）。
        只有被当前节点抢占导致跳过的原本处于 RUNNING 的节点，才会被重置。
        """
        if self._running_child is not None and self._running_child is not current_node:
            self._running_child.reset()
        self._running_child = None

    @override
    def reset(self) -> None:
        """当复合节点本身被父节点中断时，级联清理。"""
        if self._running_child is not None:
            self._running_child.reset()
            self._running_child = None

@dataclass
class Selector(Composite):
    """选择节点（OR 语义 / Fallback）。

    从左到右依次 tick 子节点：
    - 子节点返回 RUNNING → 记录为当前挂起节点，立即向上返回 RUNNING
    - 子节点返回 SUCCESS → 若之前有其他挂起节点，先调用其 reset()，
                           再向上返回 SUCCESS
    - 子节点返回 FAILURE → 继续 tick 下一个子节点
    - 所有子节点均 FAILURE → 返回 FAILURE
    """

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        for child in self.children:
            status = await child.tick(blackboard)

            if status == NodeStatus.RUNNING:
                self.set_running_child(child)
                return NodeStatus.RUNNING

            if status == NodeStatus.SUCCESS:
                self.clear_running_child(child)
                return NodeStatus.SUCCESS

        # 所有子节点均 FAILURE
        self.clear_running_child()
        return NodeStatus.FAILURE


@dataclass
class Sequence(Composite):
    """顺序节点（AND 语义）。

    从左到右依次 tick 子节点：
    - 子节点返回 RUNNING → 记录为当前挂起节点，立即向上返回 RUNNING
    - 子节点返回 FAILURE → 清理挂起节点（如有），向上返回 FAILURE
    - 子节点返回 SUCCESS → 继续 tick 下一个子节点
    - 所有子节点均 SUCCESS → 返回 SUCCESS
    """

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        for child in self.children:
            status = await child.tick(blackboard)

            if status == NodeStatus.RUNNING:
                self.set_running_child(child)   
                return NodeStatus.RUNNING

            if status == NodeStatus.FAILURE:
                self.clear_running_child(child)
                return NodeStatus.FAILURE

        self.clear_running_child()
        return NodeStatus.SUCCESS


@dataclass
class Ensure(Selector):
    """确保节点。"""

    condition: Condition
    action: Action
    children: list[BaseNode] = field(init=False)

    def __post_init__(self) -> None:
        self.children: list[BaseNode] = [self.condition, self.action]
