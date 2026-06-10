from typing import Self
from pydantic import BaseModel
from pydantic import Field


class ParsedType(BaseModel):
    origin: str
    args: tuple[Self, ...] = Field(default_factory=tuple)
