from dataclasses import dataclass
from typing import override
from code_structure.domain.aggregates.function_symbol import FunctionSymbol
from code_structure.domain.repositories.function_repository import FunctionRepository
from code_structure.infrastructure.mappers.function_node_to_function_symbol import (
    function_node_to_function_symbol,
)
from code_structure.infrastructure.mappers.function_symbol_to_function_node import (
    function_symbol_to_function_node,
)
from code_structure.infrastructure.orm_models.function_node import FunctionNode
from code_structure.domain.identities.symbol_ids import FunctionId
from foundation.persistence.sessions.neo4j_session import Neo4jSession


@dataclass
class Neo4jFunctionRepository(FunctionRepository):
    session: Neo4jSession

    @override
    def _add(self, aggregate: FunctionSymbol) -> None:
        function_node = function_symbol_to_function_node(aggregate)
        self.session.save_node(function_node)

    @override
    def _add_all(self, aggregates: list[FunctionSymbol]) -> None:
        for agg in aggregates:
            self._add(agg)

    @override
    def _save(self, aggregate: FunctionSymbol) -> None:
        function_node = function_symbol_to_function_node(aggregate)
        self.session.save_node(function_node)

    @override
    def _save_all(self, aggregates: list[FunctionSymbol]) -> None:
        for agg in aggregates:
            self._save(agg)

    @override
    def _get(self, id: FunctionId) -> FunctionSymbol:
        function_node = self.session.get(FunctionNode, str(id))
        if function_node is None:
            raise ValueError(f"Function with id {id} not found")
        function_symbol = function_node_to_function_symbol(function_node)
        return function_symbol

    @override
    def _delete(self, aggregate: FunctionSymbol) -> None:
        self.session.delete_node(node_id=str(aggregate.id))
