from __future__ import annotations
from typing import TYPE_CHECKING
from code_structure.infrastructure.orm_models.attribute_node import AttributeNode
from code_structure.infrastructure.orm_models.method_node import MethodNode
from code_structure.infrastructure.orm_models.symbol_node import SymbolNode
from foundation.persistence.orm.neo4j_base import OutNode
from pydantic import Field

if TYPE_CHECKING:
    from code_structure.infrastructure.orm_models.edges import ClassDefinesEdge


class ClassNode(SymbolNode):
    name: str
    fqn: str

    attributes: OutNode[ClassDefinesEdge, AttributeNode] = Field(
        default_factory=lambda: OutNode[ClassDefinesEdge, AttributeNode]()
    )
    methods: OutNode[ClassDefinesEdge, MethodNode] = Field(
        default_factory=lambda: OutNode[ClassDefinesEdge, MethodNode]()
    )
