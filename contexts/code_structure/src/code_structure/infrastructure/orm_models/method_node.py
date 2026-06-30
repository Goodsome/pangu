from typing import ClassVar
from foundation.persistence.orm.neo4j_base import NodeModel


class MethodNode(NodeModel):
    __labels__: ClassVar[tuple[str, ...]] = ("Method", "Symbol")

    name: str
    fqn: str
