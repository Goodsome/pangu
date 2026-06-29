from dataclasses import dataclass
from typing import override

from code_structure.application.ports.symbol_graph_admin import SymbolGraphAdmin
from neo4j import Driver


@dataclass
class Neo4jSymbolGraphAdmin(SymbolGraphAdmin):
    driver: Driver

    @override
    def purge_data(self) -> None:
        query = """
        MATCH (n:Symbol)
        DETACH DELETE n
        """
        with self.driver.session() as session:
            session.run(query)