from typing import ClassVar
from foundation.persistence.orm.neo4j_base import EdgeModel


class DefinesEdge(EdgeModel):
    __rel_type__: ClassVar[str] = "DEFINES"