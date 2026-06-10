from pydantic import BaseModel


class CodeFqn(BaseModel):
    value: str
