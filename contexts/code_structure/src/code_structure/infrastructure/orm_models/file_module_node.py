from __future__ import annotations
from code_structure.infrastructure.orm_models.class_node import ClassNode
from code_structure.infrastructure.orm_models.function_node import FunctionNode
from code_structure.infrastructure.orm_models.nodes import ModuleNode
from code_structure.infrastructure.orm_models.variable_node import VariableNode
from foundation.persistence.orm.neo4j_base import OutEdge
from code_structure.infrastructure.orm_models.symbol_node import SymbolNode
from pydantic import Field

from code_structure.infrastructure.orm_models.edges import (
    FileDefinesEdge,
    ImportsEdge,
)


class FileNode(ModuleNode):
    name: str
    fqn: str

    classes: OutEdge[FileDefinesEdge, ClassNode] = Field(default_factory=lambda: OutEdge[FileDefinesEdge, ClassNode]())
    functions: OutEdge[FileDefinesEdge, FunctionNode] = Field(default_factory=lambda: OutEdge[FileDefinesEdge, FunctionNode]())
    variables: OutEdge[FileDefinesEdge, VariableNode] = Field(default_factory=lambda: OutEdge[FileDefinesEdge, VariableNode]())
    imports: OutEdge[ImportsEdge, SymbolNode] = Field(default_factory=lambda: OutEdge[ImportsEdge, SymbolNode]())
