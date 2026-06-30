from typing import ClassVar
from foundation.persistence.orm.neo4j_base import NodeModel


class VariableNode(NodeModel):
    __labels__: ClassVar[tuple[str, ...]] = ("Variable", "Symbol")

    name: str
    fqn: str
