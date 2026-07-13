from dataclasses import dataclass
from typing import cast, override
from foundation.common_types.fqns.fqn import ClassFqn, ModuleFqn
from code_structure.domain.aggregates.class_symbol import ClassSymbol
from code_structure.domain.repositories.class_repository import ClassRepository
from code_structure.infrastructure.mappers.class_node_to_class_symbol import (
    class_node_to_class_symbol,
)
from code_structure.infrastructure.mappers.class_symbol_to_class_node import (
    class_symbol_to_class_node,
)
from code_structure.infrastructure.orm_models.class_node import ClassNode
from code_structure.domain.identities.symbol_ids import ClassId
from foundation.persistence.sessions.neo4j_session import Neo4jSession


@dataclass
class Neo4jClassRepository(ClassRepository):
    session: Neo4jSession

    @override
    def _add(self, aggregate: ClassSymbol) -> None:
        class_node = class_symbol_to_class_node(aggregate)
        self.session.save_node(class_node)

    @override
    def _add_all(self, aggregates: list[ClassSymbol]) -> None:
        for agg in aggregates:
            self._add(agg)

    @override
    def _save(self, aggregate: ClassSymbol) -> None:
        class_node = class_symbol_to_class_node(aggregate)
        self.session.save_node(class_node)

    @override
    def _save_all(self, aggregates: list[ClassSymbol]) -> None:
        for agg in aggregates:
            self._save(agg)

    @override
    def _get(self, id: ClassId) -> ClassSymbol:
        class_node = self.session.get(ClassNode, str(id))
        if class_node is None:
            raise ValueError(f"Class with id {id} not found")
        class_symbol = class_node_to_class_symbol(class_node)
        return class_symbol

    @override
    def get_by_fqn(self, fqn: ClassFqn) -> ClassSymbol:
        nodes = self.session.find(ClassNode, fqn=str(fqn))
        if not nodes:
            raise ValueError(f"Class with fqn {fqn} not found")
        class_symbol = class_node_to_class_symbol(nodes[0])
        self._seens.add(class_symbol)
        return class_symbol

    @override
    def _delete(self, aggregate: ClassSymbol) -> None:
        self.session.delete_node(node_id=str(aggregate.id))

    @override
    def find_affected_callers(self, class_id: ClassId) -> list[ModuleFqn]:
        query = (
            "MATCH (f:File)-[:DEFINES]->(s:Symbol)-[:REFERENCES]->(c:Class {id: $class_id}) "
            "RETURN DISTINCT f.fqn AS fqn"
        )
        records = self.session.execute(
            query,
            class_id=str(class_id),
        )
        return [ModuleFqn(cast(str, record["fqn"])) for record in records]

    @override
    def find_by_fqn_prefix(self, prefix: str) -> list[ClassSymbol]:
        nodes = self.session.find(ClassNode, fqn__startswith=prefix)
        symbols = [class_node_to_class_symbol(node) for node in nodes]
        for s in symbols:
            self._seens.add(s)
        return symbols
