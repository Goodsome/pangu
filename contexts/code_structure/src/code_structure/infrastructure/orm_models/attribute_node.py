from typing import ClassVar
from foundation.persistence.orm.neo4j_base import NodeModel


class AttributeNode(NodeModel):
    __labels__: ClassVar[tuple[str, ...]] = ("Attribute", "Symbol")

    name: str
    fqn: str
