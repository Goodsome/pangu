from pydantic import BaseModel


class ModuleFilter(BaseModel):
    kind: str | None = None
    name: str | None = None
    path: str | None = None
