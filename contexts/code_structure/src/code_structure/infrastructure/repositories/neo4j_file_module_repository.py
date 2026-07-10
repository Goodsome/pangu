from dataclasses import dataclass
from typing import cast, override
from code_structure.domain.aggregates.file_module import FileModule

from foundation.common_types.fqns.fqn import ModuleFqn, SymbolFqn
from code_structure.domain.value_objects.parsed_import import ParsedImport
from code_structure.domain.repositories.file_module_repository import (
    FileModuleRepository,
)
from code_structure.infrastructure.mappers.file_module_node_to_file_module import (
    file_module_node_to_file_module,
)
from code_structure.infrastructure.mappers.file_module_to_file_module_node import (
    file_module_to_file_module_node,
)
from code_structure.infrastructure.orm_models.file_module_node import FileNode
from foundation.common_types.identities.module_id import ModuleId
from foundation.persistence.sessions.neo4j_session import Neo4jSession


@dataclass
class Neo4jFileModuleRepository(FileModuleRepository):
    session: Neo4jSession

    @override
    def _add(self, aggregate: FileModule) -> None:
        file_node = file_module_to_file_module_node(aggregate)
        self.session.save_node(file_node)

    @override
    def _add_all(self, aggregates: list[FileModule]) -> None:
        for agg in aggregates:
            self._add(agg)

    @override
    def _save(self, aggregate: FileModule) -> None:
        file_node = file_module_to_file_module_node(aggregate)
        self.session.save_node(file_node)

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

    @override
    def get_external_dependencies(self, fqn: ModuleFqn) -> list[ParsedImport]:
        query = (
            "MATCH (m:File {fqn: $module_fqn})-[:DEFINES]->(s:Symbol)-[r:REFERENCES]->(ref:Symbol) "
            "WHERE NOT (m)-[:DEFINES]->(ref) "
            "RETURN DISTINCT ref.fqn AS fqn, r.alias AS alias"
        )
        records = self.session.execute(query, module_fqn=str(fqn))
        return [
            ParsedImport(
                target_fqn=SymbolFqn(cast(str, record["fqn"])),
                alias=cast(str | None, record["alias"]),
            )
            for record in records
        ]
