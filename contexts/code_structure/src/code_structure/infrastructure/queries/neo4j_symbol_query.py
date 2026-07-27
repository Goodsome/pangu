from dataclasses import dataclass
from code_structure.application.dtos.symbol_dto import SymbolDto
from code_structure.application.ports.symbol_query_service import SymbolQuery

from neo4j import Driver, ManagedTransaction

@dataclass
class Neo4jSymbolQuery(SymbolQuery):
    driver: Driver

    def find_by_names(self, names: list[str]) -> list[SymbolDto]:
        query = """
        MATCH (s:Symbol)
        WHERE s.name IN $names
        RETURN s
        """
        with self.driver.session() as session:
            def _read_tx(tx: ManagedTransaction) -> list[SymbolDto]:
                result = tx.run(query, names=names)
                return [SymbolDto(**record["s"]) for record in result]
                
            return session.execute_read(_read_tx)

    def find_aggregates_by_context(self, context: str) -> list[SymbolDto]:
        prefix = f"{context}.domain.aggregates."
        query = """
        MATCH (c:Class)
        WHERE c.fqn STARTS WITH $prefix
        RETURN c
        """
        with self.driver.session() as session:
            def _read_tx(tx: ManagedTransaction) -> list[SymbolDto]:
                result = tx.run(query, prefix=prefix)
                return [SymbolDto(**record["c"]) for record in result]

            return session.execute_read(_read_tx)