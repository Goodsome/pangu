from typing import ClassVar

from foundation.persistence.orm.neo4j_base import (
    EdgeModel,
    NodeModel,
    OutEdge,
)
from pydantic import Field


class DependsOnEdge(EdgeModel):
    __source_model__: ClassVar[type["NodeModel"] | str] = "ModuleNode"
    __target_model__: ClassVar[type["NodeModel"] | str] = "ModuleNode"


class ContainsEdge(EdgeModel):
    __source_model__: ClassVar[type["NodeModel"] | str] = "PackageNode"
    __target_model__: ClassVar[type["NodeModel"] | str] = "ModuleNode"


class ModuleNode(NodeModel): ...


class FileNode(ModuleNode):
    name: str
    fqn: str

    dependencies: OutEdge[DependsOnEdge, ModuleNode] = Field(
        default_factory=lambda: OutEdge[DependsOnEdge, ModuleNode]()
    )


class PackageNode(ModuleNode):
    name: str
    fqn: str

    contains: OutEdge[ContainsEdge, ModuleNode] = Field(
        default_factory=lambda: OutEdge[ContainsEdge, ModuleNode]()
    )
    dependencies: OutEdge[DependsOnEdge, ModuleNode] = Field(
        default_factory=lambda: OutEdge[DependsOnEdge, ModuleNode]()
    )
