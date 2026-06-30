from dataclasses import dataclass
from enum import Enum, auto
from typing import ClassVar

from pydantic import BaseModel


class NodeModel(BaseModel):
    
    _registry: ClassVar[dict[str, type['NodeModel']]] = {}
    
    __labels__: ClassVar[tuple[str, ...]]

    id: str

    @classmethod
    def __init_subclass__(cls):
        super().__init_subclass__()
        cls._registry[cls.__name__] = cls

    @classmethod
    def get_cls(cls, name: str) -> type['NodeModel']:
        if name not in cls._registry:
            raise ValueError(f"Class {name} not found in registry")
        return cls._registry[name]

class EdgeModel(BaseModel):
    __rel_type__: ClassVar[str]
    
    source_id: str
    target_id: str
    

class RelationDirection(Enum):
    IN = auto()
    OUT = auto()
    BOTH = auto()
    

@dataclass
class RelationshipMeta:
    edge_model: type[EdgeModel]
    direction: RelationDirection
    target_property: str | None = None
    target_model: type[NodeModel] | str | None = None