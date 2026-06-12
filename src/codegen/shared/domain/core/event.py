from typing import ClassVar
from pydantic import BaseModel, ConfigDict


class Event(BaseModel):
    
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")


class DomainEvent(Event):
    ...

class IntegrationEvent(Event):
    ...