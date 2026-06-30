from typing import Annotated, ClassVar
from code_structure.infrastructure.orm_models.attribute_node import AttributeNode
from code_structure.infrastructure.orm_models.defines_edge import DefinesEdge
from code_structure.infrastructure.orm_models.method_node import MethodNode
from foundation.persistence.orm.neo4j_base import NodeModel, RelationDirection, RelationshipMeta
from pydantic import Field


_ATTRIBUTES = Annotated[
    list[AttributeNode],
    RelationshipMeta(
        edge_model=DefinesEdge,
        direction=RelationDirection.OUT,
        target_model=AttributeNode,
    )
]

_METHODS = Annotated[
    list[MethodNode],
    RelationshipMeta(
        edge_model=DefinesEdge,
        direction=RelationDirection.OUT,
        target_model=MethodNode,
    )
]


class ClassNode(NodeModel):
    __labels__: ClassVar[tuple[str, ...]] = ("Class", "Symbol")

    name: str
    fqn: str

    attributes: _ATTRIBUTES = Field(default_factory=list)
    methods: _METHODS = Field(default_factory=list)