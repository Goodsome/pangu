from typing import Annotated, ClassVar
from code_structure.infrastructure.orm_models.defines_edge import DefinesEdge
from code_structure.infrastructure.orm_models.class_node import ClassNode
from code_structure.infrastructure.orm_models.function_node import FunctionNode
from code_structure.infrastructure.orm_models.variable_node import VariableNode
from foundation.persistence.orm.neo4j_base import NodeModel, RelationDirection, RelationshipMeta
from pydantic import Field

_Classes = Annotated[
    list[str],
    Field(default_factory=list),
    RelationshipMeta(
        edge_model=DefinesEdge,
        direction=RelationDirection.OUT,
        target_property="id",
        target_model=ClassNode,
    )
]

_Functions = Annotated[
    list[str],
    Field(default_factory=list),
    RelationshipMeta(
        edge_model=DefinesEdge,
        direction=RelationDirection.OUT,
        target_property="id",
        target_model=FunctionNode,
    )
]

_Variables = Annotated[
    list[str],
    Field(default_factory=list),
    RelationshipMeta(
        edge_model=DefinesEdge,
        direction=RelationDirection.OUT,
        target_property="id",
        target_model=VariableNode,
    )
]

class FileModuleNode(NodeModel):
    __labels__: ClassVar[tuple[str, ...]] = ("Module", "File")
    
    name: str
    fqn: str

    _classes: _Classes
    _functions: _Functions
    _variables: _Variables
