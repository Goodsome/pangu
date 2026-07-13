from enum import Enum, auto
from typing import ClassVar, Any, override

from foundation.common_types.snake_string import SnakeString
from pydantic import BaseModel, Field


class NodeModel(BaseModel):
    __labels__: ClassVar[tuple[str, ...]]

    _registry: ClassVar[dict[str, type["NodeModel"]]] = {}
    __edge_fields__: ClassVar[dict[str, type["Rel[Any, Any]"]]]

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

    @classmethod
    def get_edge_fields(cls) -> dict[str, type["Rel[Any, Any]"]]:
        if "__edge_fields__" in cls.__dict__:
            return cls.__edge_fields__

        edge_fields = {}
        for field_name, field_info in cls.model_fields.items():
            annotation = field_info.annotation
            if isinstance(annotation, type) and issubclass(annotation, Rel):
                edge_fields[field_name] = annotation

        cls.__edge_fields__ = edge_fields
        return edge_fields


class EdgeModel(BaseModel):
    _registry: ClassVar[dict[str, type[EdgeModel]]] = {}

    __rel_type__: ClassVar[str]
    __source_model__: ClassVar[type["NodeModel"] | str]
    __target_model__: ClassVar[type["NodeModel"] | str]

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
    def get_target_model(cls) -> type["NodeModel"]:
        if isinstance(cls.__target_model__, str):
            return NodeModel.get_cls(cls.__target_model__)
        return cls.__target_model__

    @classmethod
    def get_source_model(cls) -> type["NodeModel"]:
        if isinstance(cls.__source_model__, str):
            return NodeModel.get_cls(cls.__source_model__)
        return cls.__source_model__

    @classmethod
    def get_cls(cls, name: str) -> type[EdgeModel]:
        if name not in cls._registry:
            raise ValueError(f"Class {name} not found in registry")
        return cls._registry[name]


class RelationDirection(Enum):
    IN = auto()
    OUT = auto()
    BOTH = auto()


class ProjectionType(Enum):
    EDGE = auto()
    NODE = auto()


class EdgeItem[TEdge: EdgeModel, TTarget: NodeModel](BaseModel):
    edge: TEdge
    target: TTarget | None = None


class Rel[TEdge: EdgeModel, TTarget: NodeModel](BaseModel):
    """Base class for all relationships. Used by Query Builder for introspection."""

    items: list[EdgeItem[TEdge, TTarget]] = Field(default_factory=list)

    @classmethod
    def get_edge_cls(cls) -> type[TEdge]:
        return cls.__pydantic_generic_metadata__["args"][0]

    @classmethod
    def get_target_cls(cls) -> type[TTarget]:
        return cls.__pydantic_generic_metadata__["args"][1]

    @classmethod
    def get_direction(cls) -> RelationDirection:
        raise NotImplementedError

    @classmethod
    def get_projection_type(cls) -> ProjectionType:
        raise NotImplementedError

    def get_nodes_map(self) -> dict[str, NodeModel]:
        proj = self.get_projection_type()
        nodes_map: dict[str, NodeModel] = {}
        if proj == ProjectionType.NODE:
            for item in self.items:
                if item.target is not None:
                    nodes_map[item.target.id] = item.target
        return nodes_map

    def get_items_map(self) -> dict[str, EdgeItem[TEdge, TTarget]]:
        direction = self.get_direction()
        result: dict[str, EdgeItem[TEdge, TTarget]] = {}
        for item in self.items:
            # 提取目标节点（对方节点）的 ID
            if item.target is not None:
                other_id = item.target.id
            else:
                other_id = (
                    item.edge.source_ref
                    if direction == RelationDirection.IN
                    else item.edge.target_ref
                )
            result[other_id] = item
        return result

    def get_edges_map(self) -> dict[str, EdgeModel]:
        return {other_id: item.edge for other_id, item in self.get_items_map().items()}


class OutEdge[TEdge: EdgeModel, TTarget: NodeModel](Rel[TEdge, TTarget]):
    @classmethod
    @override
    def get_direction(cls) -> RelationDirection:
        return RelationDirection.OUT

    @classmethod
    @override
    def get_projection_type(cls) -> ProjectionType:
        return ProjectionType.EDGE


class InEdge[TEdge: EdgeModel, TTarget: NodeModel](Rel[TEdge, TTarget]):
    @classmethod
    @override
    def get_direction(cls) -> RelationDirection:
        return RelationDirection.IN

    @classmethod
    @override
    def get_projection_type(cls) -> ProjectionType:
        return ProjectionType.EDGE


class OutNode[TEdge: EdgeModel, TTarget: NodeModel](Rel[TEdge, TTarget]):
    @classmethod
    @override
    def get_direction(cls) -> RelationDirection:
        return RelationDirection.OUT

    @classmethod
    @override
    def get_projection_type(cls) -> ProjectionType:
        return ProjectionType.NODE


class InNode[TEdge: EdgeModel, TTarget: NodeModel](Rel[TEdge, TTarget]):
    @classmethod
    @override
    def get_direction(cls) -> RelationDirection:
        return RelationDirection.IN

    @classmethod
    @override
    def get_projection_type(cls) -> ProjectionType:
        return ProjectionType.NODE


class InRelation[TEdge: EdgeModel, TTarget: NodeModel](Rel[TEdge, TTarget]):
    @classmethod
    @override
    def get_direction(cls) -> RelationDirection:
        return RelationDirection.IN

    @classmethod
    @override
    def get_projection_type(cls) -> ProjectionType:
        return ProjectionType.NODE
