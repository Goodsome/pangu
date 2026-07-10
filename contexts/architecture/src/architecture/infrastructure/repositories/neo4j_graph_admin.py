from dataclasses import dataclass
from typing import override

from neo4j import Driver
from architecture.application.ports.graph_admin import GraphAdmin


@dataclass
class Neo4jGraphAdmin(GraphAdmin):
    driver: Driver

    @override
    def purge_data(self) -> None:
        query = """
        MATCH (n)
        DETACH DELETE n
        """
        with self.driver.session() as session:
            session.run(query)
