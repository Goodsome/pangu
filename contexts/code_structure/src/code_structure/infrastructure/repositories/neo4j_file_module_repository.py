from dataclasses import dataclass
from typing import override
from code_structure.domain.aggregates.file_module import FileModule
from code_structure.domain.mutations.add_defines_edge import AddModuleDefinesEdge, RemoveModuleDefinesEdge, AddModuleImportsEdge
from foundation.common_types.fqns.fqn import ModuleFqn
from code_structure.domain.repositories.file_module_repository import FileModuleRepository
from code_structure.infrastructure.mappers.file_module_node_to_file_module import file_module_node_to_file_module
from code_structure.infrastructure.orm_models.edges import FileDefinesEdge, ImportsEdge
from code_structure.infrastructure.orm_models.file_module_node import FileNode
from foundation.building_blocks.mutation_collector import Mutation
from foundation.common_types.identities.module_id import ModuleId
from foundation.persistence.sessions.neo4j_session import Neo4jSession


@dataclass
class Neo4jFileModuleRepository(FileModuleRepository):

    session: Neo4jSession

    @override
    def _add(self, aggregate: FileModule) -> None:
        self._handle_mutations(aggregate.collect_mutations())

    @override
    def _add_all(self, aggregates: list[FileModule]) -> None:
        for agg in aggregates:
            self._add(agg)

    @override
    def _save(self, aggregate: FileModule) -> None:
        self._handle_mutations(aggregate.collect_mutations())
        
    @override
    def _save_all(self, aggregates: list[FileModule]) -> None:
        for agg in aggregates:
            self._save(agg)
    
    @override
    def _get(self, id: ModuleId) -> FileModule:
        file_module_node = self.session.get(FileNode, str(id))
        if file_module_node is None:
            raise ValueError(f"Module with id {id} not found")
        file_module = file_module_node_to_file_module(file_module_node)
        return file_module

    @override
    def get_by_fqn(self, fqn: ModuleFqn) -> FileModule:
        nodes = self.session.find(FileNode, fqn=str(fqn))
        if not nodes:
            raise ValueError(f"Module with fqn {fqn} not found")
        file_module = file_module_node_to_file_module(nodes[0])
        self._seens.add(file_module)
        return file_module

    @override
    def _delete(self, aggregate: FileModule) -> None:
        raise NotImplementedError

    @override
    def get_all_modules(self) -> list[FileModule]:
        nodes = self.session.find(FileNode)
        return [file_module_node_to_file_module(node) for node in nodes]


    def _handle_mutations(self, mutations: list[Mutation]) -> None:
        for mutation in mutations:
            match mutation:
                case AddModuleDefinesEdge():
                    edge = FileDefinesEdge(
                        source_ref=str(mutation.source_id),
                        target_ref=str(mutation.target_id),
                    )
                    self.session.save_edge(edge)
                case RemoveModuleDefinesEdge():
                    edge = FileDefinesEdge(
                        source_ref=str(mutation.source_id),
                        target_ref=str(mutation.target_id),
                    )
                    self.session.delete_edge(edge)
                case AddModuleImportsEdge():
                    edge = ImportsEdge(
                        source_ref=str(mutation.source_fqn),
                        target_ref=str(mutation.target_fqn),
                        alias=mutation.alias,
                    )
                    self.session.save_edge(edge)
                case _:
                    raise NotImplementedError
        