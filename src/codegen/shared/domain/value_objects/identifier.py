from typing import Any
from typing import override
from pydantic import model_serializer
from pydantic import model_validator
from uuid import UUID
from uuid import uuid4

from foundation.building_blocks.value_object import ValueObject


class Identifier[T](ValueObject):
    value: T

    @override
    def __str__(self):
        return str(self.value)

    @override
    def __hash__(self) -> int:
        return hash(self.value)


class UuidIdentifier(Identifier[UUID]):
    """Unique identifier."""
    
    @override
    def __hash__(self) -> int:
        return hash(self.value)
        
    @classmethod
    def create(cls):
        return cls(value=uuid4())

    @classmethod
    def reconstitute(cls, value: UUID | str):
        if isinstance(value, str):
            value = UUID(value)
        return cls(value=value)

    @model_serializer
    def serialize(self) -> str:
        return str(self.value)

    @model_validator(mode="before")
    @classmethod
    def validate_from_primitive(cls, data: Any) -> Any:
        if isinstance(data, (str, UUID)):
            return {"value": data}
        return data
