from pydantic import BaseModel


class GenerateCodeCommand(BaseModel):
    fqn: str
