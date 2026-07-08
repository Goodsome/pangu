from dataclasses import dataclass
from typing import override
from code_structure.domain.aggregates.external_symbol import ExternalSymbol
from code_structure.domain.identities.symbol_ids import ExternalSymbolId
from code_structure.domain.repositories.external_symbol_repository import (
    ExternalSymbolRepository,
)
from code_structure.infrastructure.mappers.external_symbol_mapper import (
    external_symbol_node_to_external_symbol,
    external_symbol_to_external_symbol_node,
)
from code_structure.infrastructure.orm_models.external_node import ExternalNode
from foundation.common_types.fqns.fqn import SymbolFqn
from foundation.persistence.sessions.neo4j_session import Neo4jSession


@dataclass
class Neo4jExternalSymbolRepository(ExternalSymbolRepository):
    session: Neo4jSession

    @override
    def _add(self, aggregate: ExternalSymbol) -> None:
        node = external_symbol_to_external_symbol_node(aggregate)
        self.session.save_node(node)

    @override
    def _add_all(self, aggregates: list[ExternalSymbol]) -> None:
        for agg in aggregates:
            self._add(agg)

    @override
    def _save(self, aggregate: ExternalSymbol) -> None:
        node = external_symbol_to_external_symbol_node(aggregate)
        self.session.save_node(node)

    @override
    def _save_all(self, aggregates: list[ExternalSymbol]) -> None:
        for agg in aggregates:
            self._save(agg)

    @override
    def _get(self, id: ExternalSymbolId) -> ExternalSymbol:
        node = self.session.get(ExternalNode, str(id))
        if node is None:
            raise ValueError(f"ExternalSymbol with id {id} not found")
        symbol = external_symbol_node_to_external_symbol(node)
        return symbol

    @override
    def _delete(self, aggregate: ExternalSymbol) -> None:
        self.session.delete_node(node_id=str(aggregate.id))

    @override
    def get_by_fqn(self, fqn: SymbolFqn) -> ExternalSymbol:
        nodes = self.session.find(ExternalNode, fqn=str(fqn))
        if not nodes:
            raise ValueError(f"ExternalSymbol with fqn {fqn} not found")
        symbol = external_symbol_node_to_external_symbol(nodes[0])
        self._seens.add(symbol)
        return symbol
