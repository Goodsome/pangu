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
from foundation.building_blocks.mutation_collector import Mutation
from code_structure.domain.mutations.add_defines_edge import AddReferencesEdge
from code_structure.infrastructure.orm_models.edges import ReferencesEdge


@dataclass
class Neo4jVariableRepository(VariableRepository):
    session: Neo4jSession

    @override
    def _add(self, aggregate: VariableSymbol) -> None:
        variable_node = variable_symbol_to_variable_node(aggregate)
        self.session.save_node(variable_node)
        self._handle_mutations(aggregate.collect_mutations())

    @override
    def _add_all(self, aggregates: list[VariableSymbol]) -> None:
        for agg in aggregates:
            self._add(agg)

    @override
    def _save(self, aggregate: VariableSymbol) -> None:
        variable_node = variable_symbol_to_variable_node(aggregate)
        self.session.save_node(variable_node)
        self._handle_mutations(aggregate.collect_mutations())

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

    def _handle_mutations(self, mutations: list[Mutation]) -> None:
        for mutation in mutations:
            match mutation:
                case AddReferencesEdge():
                    edge = ReferencesEdge(
                        source_ref=str(mutation.source_fqn),
                        target_ref=str(mutation.target_fqn),
                    )
                    self.session.save_edge(edge)
                case _:
                    raise NotImplementedError
