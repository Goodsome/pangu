
from typing import Annotated

from code_structure.infrastructure.orm_models.defines_edge import DefinesEdge
from code_structure.infrastructure.orm_models.variable_node import VariableNode
from foundation.persistence.orm.neo4j_base import RelationDirection, RelationshipMeta
from pydantic import Field


Variables = Annotated[
    list[str],
    Field(default_factory=list),
    RelationshipMeta(
        edge_model=DefinesEdge,
        direction=RelationDirection.OUT,
        target_property="id",
        target_model=VariableNode,
    )
]
