from collections.abc import Collection
from dataclasses import dataclass
from typing import override
from architecture.infrastructure.mappers.module_to_module_node import (
    file_module_to_node,
    node_to_file_module,
)
from architecture.infrastructure.orm_models.module_node import FileNode
from foundation.common_types.fqns.fqn import ModuleFqn
from foundation.common_types.identities.module_id import ModuleId
from foundation.persistence.sessions.neo4j_session import Neo4jSession
from architecture.domain.aggregates.file_module import FileModule
from architecture.domain.repositories.file_module_repository import FileModuleRepository


@dataclass
class Neo4jFileModuleRepository(FileModuleRepository):
    session: Neo4jSession

    @override
    def _add(self, aggregate: FileModule) -> None:
        node = file_module_to_node(aggregate)
        self.session.save_node(node)

    @override
    def _add_all(self, aggregates: list[FileModule]) -> None:
        for agg in aggregates:
            self._add(agg)

    @override
    def _get(self, id: ModuleId) -> FileModule:
        node = self.session.get(FileNode, str(id))
        if node is None:
            raise ValueError(f"FileModule with id {id} not found")
        return node_to_file_module(node)

    @override
    def _save(self, aggregate: FileModule) -> None:
        node = file_module_to_node(aggregate)
        self.session.save_node(node)

    @override
    def _save_all(self, aggregates: list[FileModule]) -> None:
        for agg in aggregates:
            self._save(agg)

    @override
    def _delete(self, aggregate: FileModule) -> None:
        self.session.delete_node(node_id=str(aggregate.id))

    @override
    def delete_all(self, ids: list[ModuleId]) -> None:
        for id in ids:
            self.session.delete_node(node_id=str(id))

    @override
    def update_fqn_prefix(self, old_fqn: ModuleFqn, new_fqn: ModuleFqn) -> None:
        query = (
            " MATCH (m:Module:File)"
            " WHERE m.fqn STARTS WITH ($old_prefix + '.')"
            " SET m.fqn = $new_prefix + substring(m.fqn, size($old_prefix))"
        )
        result = self.session.execute(
            query, old_prefix=str(old_fqn), new_prefix=str(new_fqn)
        )
        result.consume()

    @override
    def find_by_fqn(self, fqn: ModuleFqn) -> FileModule | None:
        nodes = self.session.find(FileNode, fqn=str(fqn))
        if not nodes:
            return None
        module = node_to_file_module(nodes[0])
        self._seens.add(module)
        return module

    @override
    def find_by_fqns(self, fqns: Collection[ModuleFqn]) -> list[FileModule]:
        if not fqns:
            return []
        nodes = self.session.find(FileNode, fqn=[str(f) for f in fqns])
        modules: list[FileModule] = []
        for node in nodes:
            module = node_to_file_module(node)
            modules.append(module)
            self._seens.add(module)
        return modules

    @override
    def get_dependencies(self, id: ModuleId) -> list[ModuleFqn]:
        query = (
            " MATCH (target:Module:File {id: $id})"
            " MATCH (caller:Module:File)-[:DEPENDS_ON]->(target)"
            " RETURN DISTINCT caller.fqn AS caller_fqn"
        )
        result = self.session.execute(query, id=str(id))
        return [ModuleFqn(record["caller_fqn"]) for record in result]
