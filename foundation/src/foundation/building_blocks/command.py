from typing import ClassVar
from pydantic import BaseModel
from pydantic import ConfigDict


class Command(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid")
