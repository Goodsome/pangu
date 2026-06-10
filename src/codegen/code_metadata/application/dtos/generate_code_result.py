from pydantic import BaseModel


class GenerateCodeResult(BaseModel):
    code: str
