from pydantic import BaseModel


class ReverseCodeResult(BaseModel):
    component_ids: list[str]
