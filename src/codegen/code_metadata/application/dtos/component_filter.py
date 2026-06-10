from pydantic import BaseModel


class ComponentFilter(BaseModel):
    type: str | None = None
    context: str | None = None
    name: str | None = None
