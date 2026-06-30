from dataclasses import dataclass
from typing import override
from code_structure.domain.aggregates.class_symbol import ClassSymbol
from code_structure.domain.mutations.add_defines_edge import AddClassDefinesEdge
from code_structure.domain.repositories.class_repository import ClassRepository
from code_structure.infrastructure.mappers.class_node_to_class_symbol import class_node_to_class_symbol
from code_structure.infrastructure.mappers.class_symbol_to_class_node import class_symbol_to_class_node
from code_structure.infrastructure.orm_models.class_node import ClassNode
from code_structure.domain.identities.symbol_ids import ClassId
from code_structure.infrastructure.orm_models.defines_edge import DefinesEdge
from foundation.building_blocks.mutation_collector import Mutation
from foundation.persistence.sessions.neo4j_session import Neo4jSession


@dataclass
class Neo4jClassRepository(ClassRepository):

    session: Neo4jSession

    @override
    def _add(self, aggregate: ClassSymbol) -> None:
        class_node = class_symbol_to_class_node(aggregate)
        self.session.save_node(class_node)
        for attribute in class_node.attributes:
            self.session.save_node(attribute)
        for method in class_node.methods:
            self.session.save_node(method)
            
        self._handle_mutations(aggregate.collect_mutations())

    @override
    def _add_all(self, aggregates: list[ClassSymbol]) -> None:
        for agg in aggregates:
            self._add(agg)

    @override
    def _save(self, aggregate: ClassSymbol) -> None:
        class_node = class_symbol_to_class_node(aggregate)
        self.session.save_node(class_node)
        for attribute in class_node.attributes:
            self.session.save_node(attribute)
        for method in class_node.methods:
            self.session.save_node(method)
        self._handle_mutations(aggregate.collect_mutations())

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
    def _delete(self, aggregate: ClassSymbol) -> None:
        self.session.delete_node(node_id=str(aggregate.id))

    def _handle_mutations(self, mutations: list[Mutation]) -> None:
        for mutation in mutations:
            match mutation:
                case AddClassDefinesEdge():
                    edge = DefinesEdge(
                        source_id=str(mutation.source_id),
                        target_id=str(mutation.target_id),
                    )
                    self.session.save_edge(edge)
                case _:
                    raise NotImplementedError
        