from dataclasses import dataclass
from enum import Enum, auto
from typing import ClassVar

from foundation.common_types.snake_string import SnakeString
from pydantic import BaseModel


class NodeModel(BaseModel):
    
    __labels__: ClassVar[tuple[str, ...]]
    
    _registry: ClassVar[dict[str, type['NodeModel']]] = {}
    

    id: str

    @classmethod
    def __init_subclass__(cls):
        super().__init_subclass__()
        cls._registry[cls.__name__] = cls

        if "__labels__" in cls.__dict__:
            return

        calculated_labels: list[str] = []
             
        for base in cls.__mro__:
            if base in (NodeModel, BaseModel, object):
                continue
                
            name = base.__name__
            if name.endswith("Node"):
                name = name[:-4]
                
            calculated_labels.append(name)
            
        cls.__labels__ = tuple(calculated_labels)
            

    @classmethod
    def get_cls(cls, name: str) -> type[NodeModel]:
        if name not in cls._registry:
            raise ValueError(f"Class {name} not found in registry")
        return cls._registry[name]

    @classmethod
    def get_label_string(cls) -> str:
        if not cls.__labels__:
            return ""
        return ":" + ":".join(cls.__labels__)
        

class EdgeModel(BaseModel):
    
    _registry: ClassVar[dict[str, type[EdgeModel]]] = {}
    
    __rel_type__: ClassVar[str]
    __source_model__: ClassVar[type[NodeModel]]
    __target_model__: ClassVar[type[NodeModel]]
    
    __source_key__: ClassVar[str] = "id"
    __target_key__: ClassVar[str] = "id"

    source_ref: str
    target_ref: str

    @classmethod
    def __init_subclass__(cls):
        super().__init_subclass__()
        cls._registry[cls.__name__] = cls
        
        if "__rel_type__" in cls.__dict__:
            return
            
        name = cls.__name__
        if name.endswith("Edge"):
            name = name[:-4]
            
        cls.__rel_type__ = SnakeString(name).upper()

    @classmethod
    def get_target_model(cls) -> type[NodeModel]:
        return cls.__target_model__
        
    @classmethod
    def get_cls(cls, name: str) -> type[EdgeModel]:
        if name not in cls._registry:
            raise ValueError(f"Class {name} not found in registry")
        return cls._registry[name]


class RelationDirection(Enum):
    IN = auto()
    OUT = auto()
    BOTH = auto()
    

@dataclass
class RelationshipMeta:
    edge_model: str
    direction: RelationDirection = RelationDirection.OUT
    target_property: str | None = None
    target_model: type[NodeModel] | str | None = None