from dataclasses import dataclass
from typing import override
from code_structure.domain.aggregates.file_module import FileModule
from code_structure.domain.repositories.file_module_repository import FileModuleRepository
from code_structure.infrastructure.mappers.file_module_node_to_file_module import file_module_node_to_file_module
from code_structure.infrastructure.mappers.file_module_to_file_module_node import file_module_to_file_module_node
from code_structure.infrastructure.orm_models.file_module_node import FileModuleNode
from foundation.common_types.identities.module_id import ModuleId
from foundation.persistence.sessions.neo4j_session import Neo4jSession


@dataclass
class Neo4jFileModuleRepository(FileModuleRepository):

    session: Neo4jSession

    @override
    def _add(self, aggregate: FileModule) -> None:
        file_module_node = file_module_to_file_module_node(aggregate)
        self.session.save_node(file_module_node)

    @override
    def _add_all(self, aggregates: list[FileModule]) -> None:
        for agg in aggregates:
            self._add(agg)

    @override
    def _save(self, aggregate: FileModule) -> None:
        file_module_node = file_module_to_file_module_node(aggregate)
        self.session.save_node(file_module_node)
        
    @override
    def _save_all(self, aggregates: list[FileModule]) -> None:
        for agg in aggregates:
            self._save(agg)
    
    @override
    def _get(self, id: ModuleId) -> FileModule:
        file_module_node = self.session.get(FileModuleNode, str(id))
        if file_module_node is None:
            raise ValueError(f"Module with id {id} not found")
        file_module = file_module_node_to_file_module(file_module_node)
        return file_module


    @override
    def _delete(self, aggregate: FileModule) -> None:
        self.session.delete_node(node_id=str(aggregate.id))