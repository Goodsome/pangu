from foundation.persistence.orm.neo4j_base import NodeModel, OutEdge
from pydantic import Field

from code_structure.infrastructure.orm_models.edges import ReferencesEdge
from code_structure.infrastructure.orm_models.symbol_node import SymbolNode


class MemberNode(NodeModel):
    references: OutEdge[ReferencesEdge, SymbolNode] = Field(
        default_factory=lambda: OutEdge[ReferencesEdge, SymbolNode]()
    )
