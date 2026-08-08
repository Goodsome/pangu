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

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import time
from typing import override

from contextvars import ContextVar

from mhxy_automation.domain.aggregates.blackboard import Blackboard
from mhxy_automation.domain.enums.node_status import NodeStatus

logger = logging.getLogger(__name__)

_tree_depth: ContextVar[int] = ContextVar("tree_depth", default=0)


@dataclass
class BaseNode(ABC):
    """行为树节点抽象基类。"""

    node_name: str = field(default="", init=False, repr=False)
    _last_status: NodeStatus | None = field(default=None, init=False, repr=False)

    @property
    def name(self) -> str:
        if self.node_name:
            return self.node_name
        return str(self.__class__.__name__)

    async def tick(self, blackboard: Blackboard) -> NodeStatus:
        depth = _tree_depth.get()
        token = _tree_depth.set(depth + 1)
        try:
            if self._last_status != NodeStatus.RUNNING:
                indent = "  " * depth
                short_name = self.name
                if len(short_name) > 30:
                    short_name = short_name[:30] + "..."
                logger.info(f"[BT] {indent}➡️ 进入节点: {short_name}")

            # 2. 调用真正的业务逻辑
            status = await self._tick(blackboard)

            # 3. 状态跳变检测 (Edge Detection)
            # if status != self._last_status:
            self._log_status_change(status, depth)
            self._last_status = status

            return status
        finally:
            _tree_depth.reset(token)

    def _log_status_change(self, status: "NodeStatus", depth: int = 0) -> None:
        """根据不同的状态跃迁打印不同级别的日志"""
        indent = "  " * depth
        short_name = self.name
        if len(short_name) > 30:
            short_name = short_name[:30] + "..."
        if status == NodeStatus.SUCCESS:
            logger.info(f"[BT] {indent}✅ 成功: {short_name}")
        elif status == NodeStatus.FAILURE:
            logger.info(f"[BT] {indent}❌ 失败: {short_name}")
        elif status == NodeStatus.RUNNING:
            logger.info(f"[BT] {indent}⏳ 挂起: {short_name}")

    @abstractmethod
    async def _tick(self, blackboard: Blackboard) -> NodeStatus:
        """执行本节点逻辑，返回当前帧的执行状态。"""
        ...

    def reset(self) -> None:
        """【框架级方法】重置状态并调用子类清理逻辑。"""
        if self._last_status is not None:
            logger.debug(f"[BT] 🔄 中断/重置: {self.name}")
            self._last_status = None
        self._reset()

    def _reset(self) -> None:
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
class Not(Condition):
    """否定条件节点。"""

    condition: Condition

    @property
    @override
    def name(self) -> str:
        return f"Not({self.condition.name})"

    @override
    async def _tick(self, blackboard: Blackboard) -> NodeStatus:
        result = await self.condition.tick(blackboard)
        return (
            NodeStatus.FAILURE if result == NodeStatus.SUCCESS else NodeStatus.SUCCESS
        )


@dataclass
class Action(BaseNode, ABC):
    """动作节点。"""


@dataclass
class RunningAction(BaseNode, ABC):
    expire_time: float = field(default=0.0)
    _start_time: float = field(default=0.0, init=False, repr=False)
    _is_active: bool = field(default=False, init=False, repr=False)

    @override
    async def _tick(self, blackboard: Blackboard) -> NodeStatus:
        now = time.monotonic()

        if not self._is_active:
            self._start_time = now
            self._is_active = True
            await self.on_start(blackboard)
            return NodeStatus.RUNNING

        # 2. 超时检测
        if self.expire_time > 0:
            if now - self._start_time > self.expire_time:
                logger.warning(
                    f"[Timeout] 动作 {self.name} 已超过 {self.expire_time} 秒，强制失败"
                )
                self._is_active = False
                return NodeStatus.FAILURE

        # 3. 运行状态反馈检测（核心：指令还在生效吗？）
        status = await self.on_update(blackboard)

        # 如果动作自然结束（成功或失败），重置活跃状态以便下次重新触发
        if status != NodeStatus.RUNNING:
            self._is_active = False

        return status

    @override
    def _reset(self) -> None:
        self._is_active = False
        self.on_reset()

    @abstractmethod
    async def on_start(self, blackboard: Blackboard) -> None:
        """
        动作首次执行时调用。
        【职责】：发送游戏指令（如：鼠标点击目标坐标、按下快捷键）。
        """
        pass

    @abstractmethod
    async def on_update(self, blackboard: Blackboard) -> NodeStatus:
        """
        动作持续期间每帧调用。
        【职责】：校验物理状态（如：检测角色是否在移动、读条是否还在继续）。
        【返回】：
            - RUNNING: 动作还在健康地持续中。
            - SUCCESS: 动作已完成（例如：角色物理上停下来了）。
            - FAILURE: 发现异常中断（例如：预期在移动，但发现并未移动）。
        """
        pass

    def on_reset(self) -> None:
        """子类可选实现：被打断时的清理逻辑（如：发送停止移动的指令）。"""
        pass


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
    def _reset(self) -> None:
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
    async def _tick(self, blackboard: Blackboard) -> NodeStatus:
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
    async def _tick(self, blackboard: Blackboard) -> NodeStatus:
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
class MemorySequence(Composite):
    """记忆顺序节点 (Sequence*)。

    一旦子节点返回 SUCCESS，就会推进内部游标。
    下一帧 tick 时，直接从游标指向的节点开始执行，不再重新评估之前的节点。
    """

    _current_index: int = field(default=0, init=False, repr=False)

    @override
    async def _tick(self, blackboard: "Blackboard") -> NodeStatus:
        # 从当前记忆的索引开始执行
        while self._current_index < len(self.children):
            child = self.children[self._current_index]
            status = await child.tick(blackboard)

            if status == NodeStatus.RUNNING:
                self.set_running_child(child)
                return NodeStatus.RUNNING

            if status == NodeStatus.FAILURE:
                # 关键：一旦失败，流水线断裂，重置游标，并向上返回失败
                self.clear_running_child(child)
                self._current_index = 0
                return NodeStatus.FAILURE

            if status == NodeStatus.SUCCESS:
                # 节点成功，推进游标，并继续 while 循环执行下一个节点
                self.clear_running_child(child)
                self._current_index += 1

        # 所有子节点都成功执行完毕，重置游标，为下一次整树执行做准备
        self._current_index = 0
        return NodeStatus.SUCCESS

    @override
    def _reset(self) -> None:
        """重置状态与游标"""
        super()._reset()
        self._current_index = 0


@dataclass
class Ensure(Selector):
    """确保节点。"""

    condition: Condition
    action: Action | RunningAction
    children: list[BaseNode] = field(init=False)

    def __post_init__(self) -> None:
        self.children = [self.condition, self.action]

    @override
    async def _tick(self, blackboard: Blackboard) -> NodeStatus:
        # 1. 优先评估条件
        cond_status = await self.condition.tick(blackboard)

        if cond_status == NodeStatus.SUCCESS:
            # 目标已达成！如果 action 还在挂起，立刻打断它
            if self._running_child is self.action:
                self.action.reset()
                self._running_child = None
            return NodeStatus.SUCCESS

        # 2. 目标未达成，执行动作
        action_status = await self.action.tick(blackboard)

        if action_status == NodeStatus.RUNNING:
            self._running_child = self.action
        else:
            self.clear_running_child(self.action)

        return NodeStatus.RUNNING


@dataclass
class When(Sequence):
    """当节点。"""

    condition: Condition
    action: Action
    children: list[BaseNode] = field(init=False)

    def __post_init__(self) -> None:
        self.children = [self.condition, self.action]

    @property
    @override
    def name(self) -> str:
        return f"When({self.condition.name}, {self.action.name})"


@dataclass
class IfThenElse(BaseNode):
    """标准三元控制流节点。"""

    condition: Condition
    if_node: BaseNode
    else_node: BaseNode

    _running_child: BaseNode | None = field(default=None, init=False, repr=False)

    @override
    async def _tick(self, blackboard: "Blackboard") -> NodeStatus:
        # 1. 评估条件（每帧仅评估一次）
        cond_status = await self.condition.tick(blackboard)

        if cond_status == NodeStatus.SUCCESS:
            # 抢占清理：如果上一帧还在执行 else 分支，现在条件满足了，打断 else
            if self._running_child is self.else_node:
                self.else_node.reset()

            # 执行 if 分支
            status = await self.if_node.tick(blackboard)
            self._running_child = self.if_node if status == NodeStatus.RUNNING else None
            return status

        elif cond_status == NodeStatus.FAILURE:
            # 抢占清理：如果上一帧还在执行 if 分支，现在条件不满足了，打断 if
            if self._running_child is self.if_node:
                self.if_node.reset()

            # 执行 else 分支
            status = await self.else_node.tick(blackboard)
            self._running_child = (
                self.else_node if status == NodeStatus.RUNNING else None
            )
            return status

        else:
            # cond_status == NodeStatus.RUNNING (极少数情况 condition 本身需要跨帧)
            if (
                self._running_child is not None
                and self._running_child is not self.condition
            ):
                self._running_child.reset()
            self._running_child = self.condition
            return NodeStatus.RUNNING

    @override
    def _reset(self) -> None:
        if self._running_child is not None:
            self._running_child.reset()
            self._running_child = None
