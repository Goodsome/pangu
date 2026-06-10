from pydantic import BaseModel


class ReverseCodeCommand(BaseModel):
    context: str
    component_type: str | None = None
