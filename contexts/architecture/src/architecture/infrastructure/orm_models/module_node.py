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

    dependencies: Dependencies


class PackageNode(NodeModel):
    __labels__: ClassVar[tuple[str, ...]] = ("Module", "Package")

    name: str

    contains: Contains

    dependencies: Dependencies
