from pydantic import BaseModel


class Page[T](BaseModel):
    items: list[T]
    total: int
    current: int
    size: int | None


class PageQuery[T](BaseModel):
    current: int = 1
    size: int | None = 10
    condition: T
    
