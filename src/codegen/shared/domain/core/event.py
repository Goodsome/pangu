from datetime import datetime
from datetime import timezone
from typing import ClassVar
from uuid import UUID
from uuid import uuid4
from pydantic import BaseModel
from pydantic import Field
from pydantic import ConfigDict


class Event(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")


class DomainEvent(Event):
    pass


class IntegrationEvent(Event):
    __domain_entity__: ClassVar[str]
    event_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def topic(cls) -> str:
        return f"{cls.__domain_entity__}_events"

    @property
    def event_type_name(self) -> str:
        """当前事件的具体类名，用于 MQ 消费者反序列化。"""
        return type(self).__name__
