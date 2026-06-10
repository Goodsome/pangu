from pydantic import BaseModel


class DeleteComponentCommand(BaseModel):
    component_id: str
