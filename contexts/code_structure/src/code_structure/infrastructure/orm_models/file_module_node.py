from typing import Annotated
from code_structure.infrastructure.orm_models.class_node import ClassNode
from code_structure.infrastructure.orm_models.function_node import FunctionNode
from code_structure.infrastructure.orm_models.nodes import ModuleNode
from code_structure.infrastructure.orm_models.variable_node import VariableNode
from foundation.persistence.orm.neo4j_base import RelationshipMeta
from pydantic import Field

_Classes = Annotated[
    list[str],
    RelationshipMeta(
        edge_model="FileDefinesEdge",
        target_property="id",
        target_model=ClassNode,
    )
]

_Functions = Annotated[
    list[str],
    RelationshipMeta(
        edge_model="FileDefinesEdge",
        target_property="id",
        target_model=FunctionNode,
    )
]

_Variables = Annotated[
    list[str],
    Field(default_factory=list),
    RelationshipMeta(
        edge_model="FileDefinesEdge",
        target_property="id",
        target_model=VariableNode,
    )
]


class FileNode(ModuleNode):
    
    name: str
    fqn: str

    classes: _Classes = Field(default_factory=list)
    functions: _Functions = Field(default_factory=list)
    variables: _Variables = Field(default_factory=list)
