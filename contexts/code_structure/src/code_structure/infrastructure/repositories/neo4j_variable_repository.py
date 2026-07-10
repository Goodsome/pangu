from dataclasses import dataclass
from typing import override
from code_structure.domain.aggregates.variable_symbol import VariableSymbol
from code_structure.domain.repositories.variable_repository import VariableRepository
from code_structure.infrastructure.mappers.variable_node_to_variable_symbol import (
    variable_node_to_variable_symbol,
)
from code_structure.infrastructure.mappers.variable_symbol_to_variable_node import (
    variable_symbol_to_variable_node,
)
from code_structure.infrastructure.orm_models.variable_node import VariableNode
from code_structure.domain.identities.symbol_ids import VariableId
from foundation.persistence.sessions.neo4j_session import Neo4jSession


@dataclass
class Neo4jVariableRepository(VariableRepository):
    session: Neo4jSession

    @override
    def _add(self, aggregate: VariableSymbol) -> None:
        variable_node = variable_symbol_to_variable_node(aggregate)
        self.session.save_node(variable_node)

    @override
    def _add_all(self, aggregates: list[VariableSymbol]) -> None:
        for agg in aggregates:
            self._add(agg)

    @override
    def _save(self, aggregate: VariableSymbol) -> None:
        variable_node = variable_symbol_to_variable_node(aggregate)
        self.session.save_node(variable_node)

    @override
    def _save_all(self, aggregates: list[VariableSymbol]) -> None:
        for agg in aggregates:
            self._save(agg)

    @override
    def _get(self, id: VariableId) -> VariableSymbol:
        variable_node = self.session.get(VariableNode, str(id))
        if variable_node is None:
            raise ValueError(f"Variable with id {id} not found")
        variable_symbol = variable_node_to_variable_symbol(variable_node)
        return variable_symbol

    @override
    def _delete(self, aggregate: VariableSymbol) -> None:
        self.session.delete_node(node_id=str(aggregate.id))

    @override
    def find_by_fqn_prefix(self, prefix: str) -> list[VariableSymbol]:
        nodes = self.session.find(VariableNode, fqn__startswith=prefix)
        symbols = [variable_node_to_variable_symbol(node) for node in nodes]
        for s in symbols:
            self._seens.add(s)
        return symbols

