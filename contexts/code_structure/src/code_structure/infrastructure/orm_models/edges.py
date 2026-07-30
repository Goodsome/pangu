from typing import ClassVar
from foundation.persistence.orm.neo4j_base import EdgeModel, NodeModel


class ImportsEdge(EdgeModel):
    __source_key__: ClassVar[str] = "fqn"
    __target_key__: ClassVar[str] = "fqn"
    __source_model__: ClassVar[type["NodeModel"] | str] = "FileNode"
    __target_model__: ClassVar[type["NodeModel"] | str] = "SymbolNode"

    alias: str | None = None


class ReferencesEdge(EdgeModel):
    __source_key__: ClassVar[str] = "fqn"
    __target_key__: ClassVar[str] = "fqn"
    __source_model__: ClassVar[type["NodeModel"] | str] = "SymbolNode"
    __target_model__: ClassVar[type["NodeModel"] | str] = "SymbolNode"

    alias: str | None = None


class FileDefinesEdge(EdgeModel):
    __rel_type__: ClassVar[str] = "DEFINES"
    __source_key__: ClassVar[str] = "id"
    __target_key__: ClassVar[str] = "id"
    __source_model__: ClassVar[type["NodeModel"] | str] = "FileNode"
    __target_model__: ClassVar[type["NodeModel"] | str] = "SymbolNode"


class ClassDefinesEdge(EdgeModel):
    __rel_type__: ClassVar[str] = "DEFINES"
    __source_key__: ClassVar[str] = "id"
    __target_key__: ClassVar[str] = "id"
    __source_model__: ClassVar[type["NodeModel"] | str] = "ClassNode"
    __target_model__: ClassVar[type["NodeModel"] | str] = "MemberNode"
