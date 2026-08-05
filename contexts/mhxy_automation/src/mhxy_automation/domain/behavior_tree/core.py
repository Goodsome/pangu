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
class Selector(BaseNode):
    """选择节点（OR 语义 / Fallback）。

    从左到右依次 tick 子节点：
    - 子节点返回 RUNNING → 记录为当前挂起节点，立即向上返回 RUNNING
    - 子节点返回 SUCCESS → 若之前有其他挂起节点，先调用其 reset()，
                           再向上返回 SUCCESS
    - 子节点返回 FAILURE → 继续 tick 下一个子节点
    - 所有子节点均 FAILURE → 返回 FAILURE
    """

    children: list[BaseNode]
    _running_child: BaseNode | None = field(default=None, init=False, repr=False)

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        for child in self.children:
            status = await child.tick(blackboard)

            if status == NodeStatus.RUNNING:
                # 若切换到了不同的子节点处于 RUNNING，先 reset 旧的挂起节点
                if self._running_child is not None and self._running_child is not child:
                    self._running_child.reset()
                self._running_child = child
                return NodeStatus.RUNNING

            if status == NodeStatus.SUCCESS:
                # 高优先级子节点成功，若之前有其他节点挂在 RUNNING，通知其 reset
                if self._running_child is not None and self._running_child is not child:
                    self._running_child.reset()
                self._running_child = None
                return NodeStatus.SUCCESS

        # 所有子节点均 FAILURE
        self._running_child = None
        return NodeStatus.FAILURE

    @override
    def reset(self) -> None:
        """级联重置挂起的子节点。"""
        if self._running_child is not None:
            self._running_child.reset()
            self._running_child = None


@dataclass
class Sequence(BaseNode):
    """顺序节点（AND 语义）。

    从左到右依次 tick 子节点：
    - 子节点返回 RUNNING → 记录为当前挂起节点，立即向上返回 RUNNING
    - 子节点返回 FAILURE → 清理挂起节点（如有），向上返回 FAILURE
    - 子节点返回 SUCCESS → 继续 tick 下一个子节点
    - 所有子节点均 SUCCESS → 返回 SUCCESS
    """

    children: list[BaseNode]
    _running_child: BaseNode | None = field(default=None, init=False, repr=False)

    @override
    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        for child in self.children:
            status = await child.tick(blackboard)

            if status == NodeStatus.RUNNING:
                self._running_child = child
                return NodeStatus.RUNNING

            if status == NodeStatus.FAILURE:
                self._running_child = None
                return NodeStatus.FAILURE

        self._running_child = None
        return NodeStatus.SUCCESS

    @override
    def reset(self) -> None:
        """级联重置挂起的子节点。"""
        if self._running_child is not None:
            self._running_child.reset()
            self._running_child = None
