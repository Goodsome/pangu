from typing import Annotated
from code_structure.infrastructure.orm_models.attribute_node import AttributeNode
from code_structure.infrastructure.orm_models.method_node import MethodNode
from code_structure.infrastructure.orm_models.symbol_node import SymbolNode
from foundation.persistence.orm.neo4j_base import RelationDirection, RelationshipMeta
from pydantic import Field


_ATTRIBUTES = Annotated[
    list[AttributeNode],
    RelationshipMeta(
        edge_model="ClassDefinesEdge",
        direction=RelationDirection.OUT,
        target_model=AttributeNode,
    ),
]

_METHODS = Annotated[
    list[MethodNode],
    RelationshipMeta(
        edge_model="ClassDefinesEdge",
        direction=RelationDirection.OUT,
        target_model=MethodNode,
    ),
]


class ClassNode(SymbolNode):
    name: str
    fqn: str

    attributes: _ATTRIBUTES = Field(default_factory=list)
    methods: _METHODS = Field(default_factory=list)
