from dataclasses import dataclass
from typing import override

from code_structure.application.ports.symbol_graph_admin import SymbolGraphAdmin
from foundation.persistence.sessions.neo4j_session import Neo4jSession


@dataclass
class Neo4jSymbolGraphAdmin(SymbolGraphAdmin):
    session: Neo4jSession

    @override
    def purge_data(self) -> None:
        self.session.execute("MATCH (n:Symbol) DETACH DELETE n")
