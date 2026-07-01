from typing import Annotated, ClassVar

from foundation.persistence.orm.neo4j_base import (
    EdgeModel,
    NodeModel,
    RelationshipMeta,
)
from pydantic import Field


Dependencies = Annotated[
    list[str],
    Field(default_factory=list),
    RelationshipMeta(
        edge_model="DependsOnEdge",
        target_property="id",
    ),
]

Contains = Annotated[
    list[str],
    Field(default_factory=list),
    RelationshipMeta(
        edge_model="ContainsEdge",
        target_property="id",
    ),
]

class ModuleNode(NodeModel):
    ...
    

class FileNode(ModuleNode):

    name: str
    fqn: str

    dependencies: Dependencies


class PackageNode(ModuleNode):

    name: str
    fqn: str

    contains: Contains

    dependencies: Dependencies


class DependsOnEdge(EdgeModel):
    __source_model__: ClassVar[type[NodeModel]] = ModuleNode
    __target_model__: ClassVar[type[NodeModel]] = FileNode
    

class ContainsEdge(EdgeModel):
    __source_model__: ClassVar[type[NodeModel]] = PackageNode
    __target_model__: ClassVar[type[NodeModel]] = ModuleNode
