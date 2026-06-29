from typing import ClassVar
from foundation.persistence.orm.neo4j_base import NodeModel


class VariableNode(NodeModel):
    __labels__: ClassVar[tuple[str, ...]] = ("Variable",)

    name: str
    fqn: str
    start_line: int
    start_column: int
    end_line: int
    end_column: int
