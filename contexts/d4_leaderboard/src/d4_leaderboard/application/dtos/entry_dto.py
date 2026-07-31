from uuid import UUID
from pydantic import BaseModel


class EntryDto(BaseModel):
    id: UUID
    name: str
