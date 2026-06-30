from typing import Annotated, ClassVar
from code_structure.infrastructure.orm_models.defines_edge import DefinesEdge
from code_structure.infrastructure.orm_models.class_node import ClassNode
from code_structure.infrastructure.orm_models.function_node import FunctionNode
from code_structure.infrastructure.orm_models.variables import Variables
from foundation.persistence.orm.neo4j_base import NodeModel, RelationDirection, RelationshipMeta
from pydantic import Field

_Classes = Annotated[
    list[str],
    RelationshipMeta(
        edge_model=DefinesEdge,
        direction=RelationDirection.OUT,
        target_property="id",
        target_model=ClassNode,
    )
]

_Functions = Annotated[
    list[str],
    RelationshipMeta(
        edge_model=DefinesEdge,
        direction=RelationDirection.OUT,
        target_property="id",
        target_model=FunctionNode,
    )
]

class FileModuleNode(NodeModel):
    __labels__: ClassVar[tuple[str, ...]] = ("Module", "File")
    
    name: str
    fqn: str

    classes: _Classes = Field(default_factory=list)
    functions: _Functions = Field(default_factory=list)
    variables: Variables = Field(default_factory=list)
