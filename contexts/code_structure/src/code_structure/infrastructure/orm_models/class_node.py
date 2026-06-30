from typing import ClassVar
from foundation.persistence.orm.neo4j_base import NodeModel


class ClassNode(NodeModel):
    __labels__: ClassVar[tuple[str, ...]] = ("Class", "Symbol")

    name: str
    fqn: str
