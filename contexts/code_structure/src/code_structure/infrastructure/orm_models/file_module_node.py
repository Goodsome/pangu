from typing import ClassVar
from foundation.persistence.orm.neo4j_base import NodeModel

class FileModuleNode(NodeModel):
    __labels__: ClassVar[tuple[str, ...]] = ("Module", "File")
    
    name: str
    fqn: str