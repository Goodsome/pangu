from pydantic import BaseModel


class PageQuery[T](BaseModel):
    current: int = 1
    size: int | None = 10
    condition: T
