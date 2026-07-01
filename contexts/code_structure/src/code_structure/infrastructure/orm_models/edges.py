from typing import ClassVar
from code_structure.infrastructure.orm_models.class_node import ClassNode
from code_structure.infrastructure.orm_models.file_module_node import FileNode
from code_structure.infrastructure.orm_models.symbol_node import SymbolNode
from foundation.persistence.orm.neo4j_base import EdgeModel, NodeModel


class ReferencesEdge(EdgeModel):
    __source_key__: ClassVar[str] = "fqn"
    __target_key__: ClassVar[str] = "fqn"
    __source_model__: ClassVar[type[NodeModel]] = SymbolNode
    __target_model__: ClassVar[type[NodeModel]] = SymbolNode


class FileDefinesEdge(EdgeModel):
    __rel_type__: ClassVar[str] = "DEFINES"
    __source_key__: ClassVar[str] = "id"
    __target_key__: ClassVar[str] = "id"
    __source_model__: ClassVar[type[NodeModel]] = FileNode
    __target_model__: ClassVar[type[NodeModel]] = SymbolNode

class ClassDefinesEdge(EdgeModel):
    __rel_type__: ClassVar[str] = "DEFINES"
    __source_key__: ClassVar[str] = "id"
    __target_key__: ClassVar[str] = "id"
    __source_model__: ClassVar[type[NodeModel]] = ClassNode
    __target_model__: ClassVar[type[NodeModel]] = SymbolNode