from foundation.persistence.orm.neo4j_base import NodeModel, OutEdge
from pydantic import Field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from code_structure.infrastructure.orm_models.edges import ReferencesEdge


class SymbolNode(NodeModel):
    references: OutEdge[ReferencesEdge, SymbolNode] = Field(
        default_factory=lambda: OutEdge[ReferencesEdge, SymbolNode]()
    )
