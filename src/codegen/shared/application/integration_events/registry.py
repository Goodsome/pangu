from dataclasses import dataclass
from dataclasses import field
import logging
from codegen.shared.application.integration_events.batch_nodes_deleted import (
    BatchNodesDeletedIntegrationEvent,
)
from codegen.shared.application.integration_events.node_moved import (
    NodeMovedIntegrationEvent,
)
from codegen.shared.domain.core.event import IntegrationEvent
from codegen.shared.application.integration_events.node_deleted import (
    NodeDeletedIntegrationEvent,
)

logger = logging.getLogger("event_hub.registry")


@dataclass
class EventRegistry:
    """集成事件类型注册表。"""

    _entries: dict[str, type[IntegrationEvent]] = field(default_factory=dict)

    def register(self, event_class: type[IntegrationEvent]) -> None:
        """注册一个集成事件类型。"""
        name = event_class.__name__
        if name in self._entries:
            existing = self._entries[name]
            if existing is not event_class:
                logger.warning(
                    "⚠️ 事件类型 %r 已注册为 %s，将被覆盖为 %s",
                    name,
                    existing.__module__,
                    event_class.__module__,
                )
        self._entries[name] = event_class
        logger.debug("📋 注册事件类型: %s → %s", name, event_class)

    def resolve(self, event_type_name: str) -> type[IntegrationEvent] | None:
        """根据事件类型名称查找对应的 Python 类。

        Returns:
            找到则返回事件类，否则返回 None。
        """
        return self._entries.get(event_type_name)

    @property
    def registered_types(self) -> list[str]:
        """返回所有已注册的事件类型名称。"""
        return list(self._entries.keys())

    @classmethod
    def init(cls) -> EventRegistry:
        registry = cls()
        registry.register(NodeDeletedIntegrationEvent)
        registry.register(BatchNodesDeletedIntegrationEvent)
        registry.register(NodeMovedIntegrationEvent)
        return registry
