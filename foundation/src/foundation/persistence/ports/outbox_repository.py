from abc import ABC, abstractmethod
from foundation.building_blocks.event import IntegrationEvent


class OutboxRepository(ABC):
    """Outbox 发件箱仓储端口抽象"""

    @abstractmethod
    def save(self, message: IntegrationEvent) -> None:
        """保存 Outbox 集成事件消息"""
        pass
