from typing import Annotated

from foundation.persistence.orm.neo4j_base import RelationshipMeta


Dependencies = Annotated[
    list[str],
    RelationshipMeta(
        edge_model="ReferencesEdge",
        target_property="fqn",
    )
]