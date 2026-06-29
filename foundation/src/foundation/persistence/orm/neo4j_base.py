from dataclasses import dataclass
from enum import Enum, auto
from typing import ClassVar

from pydantic import BaseModel


class NodeModel(BaseModel):
    
    __labels__: ClassVar[tuple[str, ...]]

    id: str

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
    target_property: str