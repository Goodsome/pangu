from typing import Annotated, ClassVar

from foundation.persistence.orm.neo4j_base import (
    EdgeModel,
    NodeModel,
    RelationDirection,
    RelationshipMeta,
)
from pydantic import Field


class DependsOnEdge(EdgeModel):
    __rel_type__: ClassVar[str] = "DEPENDS_ON"


class ContainsEdge(EdgeModel):
    __rel_type__: ClassVar[str] = "CONTAINS"


Dependencies = Annotated[
    list[str],
    Field(default_factory=list),
    RelationshipMeta(
        edge_model=DependsOnEdge,
        direction=RelationDirection.OUT,
        target_property="id",
        target_model="FileModuleNode",
    ),
]

Contains = Annotated[
    list[str],
    Field(default_factory=list),
    RelationshipMeta(
        edge_model=ContainsEdge,
        direction=RelationDirection.OUT,
        target_property="id",
    ),
]


class FileModuleNode(NodeModel):
    __labels__: ClassVar[tuple[str, ...]] = ("Module", "File")

    name: str
    fqn: str

    dependencies: Dependencies


class PackageModuleNode(NodeModel):
    __labels__: ClassVar[tuple[str, ...]] = ("Module", "Package")

    name: str
    fqn: str

    contains: Contains

    dependencies: Dependencies

ModuleNode = FileModuleNode | PackageModuleNode