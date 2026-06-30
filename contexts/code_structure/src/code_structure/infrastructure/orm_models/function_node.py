from typing import ClassVar
from foundation.persistence.orm.neo4j_base import NodeModel


class FunctionNode(NodeModel):
    __labels__: ClassVar[tuple[str, ...]] = ("Function", "Symbol")

    name: str
    fqn: str
