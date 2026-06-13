from typing import ClassVar
from pydantic import BaseModel
from pydantic import ConfigDict


class Event(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")


class DomainEvent(Event):
    pass


class IntegrationEvent(Event):
    pass
