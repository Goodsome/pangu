from dataclasses import dataclass
from architecture.domain.aggregates.module import Module
from architecture.domain.identities.module_id import ModuleId
from architecture.domain.mutasions.add_contains_edge import AddContainsEdgeMutation
from architecture.domain.mutasions.add_depends_on_edge import AddDependsEdgeMutation
from architecture.domain.mutasions.remove_contains_edge import (
    RemoveContainsEdgeMutation,
)
from architecture.domain.mutasions.remove_depends_on_edge import (
    RemoveDependsEdgeMutation,
)
from architecture.domain.repositories.module_repository import ModuleRepository
from typing import override
from neo4j import Transaction
from architecture.domain.value_objects.fqn import ModuleFqn
from foundation.building_blocks.mutation_collector import Mutation


@dataclass
class Neo4jModuleRepository(ModuleRepository):
    transaction: Transaction

    @override
    def _add(self, aggregate: Module) -> None:
        query = "\n        CREATE (m {\n            id: $id,\n            fqn: $fqn,\n            name: $name\n        })\n        WITH m\n        CALL {\n            WITH m\n            WITH m, $is_package AS is_pkg\n            WHERE is_pkg\n            SET m:Package\n        }\n        CALL {\n            WITH m\n            WITH m, $is_package AS is_pkg\n            WHERE NOT is_pkg\n            SET m:File\n        }\n        "
        self.transaction.run(
            query,
            id=str(aggregate.id),
            fqn=str(aggregate.fqn),
            name=aggregate.name,
            is_package=aggregate.is_package,
        )
        self._batch_handle_mutations(aggregate.collect_mutations())

    @override
    def _add_all(self, aggregates: list[Module]) -> None:
        if not aggregates:
            return
        query = "\n        UNWIND $modules AS mod\n        CREATE (m:Module {\n            id: mod.id,\n            fqn: mod.fqn,\n            name: mod.name\n        })\n        FOREACH (_ IN CASE WHEN mod.is_package THEN [1] ELSE [] END |\n            SET m:Package\n        )\n        \n        FOREACH (_ IN CASE WHEN NOT mod.is_package THEN [1] ELSE [] END |\n            SET m:File\n        )\n        "
        modules_data: list[dict[str, object]] = []
        mutations: list[Mutation] = []
        for agg in aggregates:
            modules_data.append(self._aggregate_to_dict(agg))
            mutations.extend(agg.collect_mutations())
        self.transaction.run(query, modules=modules_data)
        self._batch_handle_mutations(mutations)

    @override
    def _get(self, id: ModuleId) -> Module:
        query = '\n        MATCH (m:Module {id: $id})\n        OPTIONAL MATCH (m)-[:DEPENDS_ON]->(target:Module)\n        OPTIONAL MATCH (m)-[:CONTAINS]->(child:Module)\n        RETURN \n            m, \n            "Package" IN labels(m) AS is_package,\n            collect(DISTINCT target.id) AS dependencies,\n            collect(DISTINCT child.id) AS contains\n        '
        result = self.transaction.run(query, id=str(id)).single()
        if not result:
            raise ValueError(f"Module with id {id} not found")
        node = result["m"]
        dependencies = result["dependencies"]
        contains = result["contains"]
        module = Module.reconstitute(
            module_id=node["id"],
            fqn=node["fqn"],
            name=node["name"],
            is_package=result["is_package"],
            dependencies=dependencies,
            contains=contains,
        )
        return module

    @override
    def _save(self, aggregate: Module) -> None:
        query = "\n        MERGE (m:Module {id: $id})\n        SET m.fqn = $fqn,\n            m.name = $name\n        "
        self.transaction.run(
            query, id=str(aggregate.id), fqn=str(aggregate.fqn), name=aggregate.name
        )
        self._batch_handle_mutations(aggregate.collect_mutations())

    @override
    def _save_all(self, aggregates: list[Module]) -> None:
        if not aggregates:
            return
        query = "\n        UNWIND $modules AS mod\n        MERGE (m:Module {id: mod.id})\n        SET m.fqn = mod.fqn,\n            m.name = mod.name,\n        "
        modules_data: list[dict[str, object]] = []
        mutations: list[Mutation] = []
        for agg in aggregates:
            modules_data.append(self._aggregate_to_dict(agg))
            mutations.extend(agg.collect_mutations())
        self.transaction.run(query, modules=modules_data)
        self._batch_handle_mutations(mutations)

    @override
    def _delete(self, aggregate: Module) -> None:
        query = (
            "\n        MATCH (m:Module {id: $id})\n        DETACH DELETE m\n        "
        )
        self.transaction.run(query, id=str(aggregate.id))

    @override
    def delete_all(self, ids: list[ModuleId]) -> None:
        if not ids:
            return
        query = "\n        UNWIND $batch_ids AS mod_id\n        MATCH (m:Module {id: mod_id})\n        DETACH DELETE m\n        "
        self.transaction.run(query, batch_ids=[str(id) for id in ids])

    def _aggregate_to_dict(self, aggregate: Module) -> dict[str, object]:
        """辅助方法：将 Aggregate Root 序列化为 Cypher UNWIND 兼容的字典"""
        return {
            "id": str(aggregate.id),
            "fqn": str(aggregate.fqn),
            "name": aggregate.name,
            "is_package": aggregate.is_package,
        }

    def _batch_add_depends_on_edges(self, mutations: list[Mutation]):
        batch_data = [
            m.model_dump() for m in mutations if isinstance(m, AddDependsEdgeMutation)
        ]
        if not batch_data:
            return
        merge_query = "\n        UNWIND $batch AS edge\n        MATCH (s:Module {id: edge.source}), (t:Module {id: edge.target})\n        MERGE (s)-[:DEPENDS_ON]->(t)\n        "
        self.transaction.run(merge_query, batch=batch_data)

    def _batch_remove_depends_on_edges(self, mutations: list[Mutation]):
        batch_data = [
            m.model_dump()
            for m in mutations
            if isinstance(m, RemoveDependsEdgeMutation)
        ]
        if not batch_data:
            return
        merge_query = "\n        UNWIND $batch AS edge\n        MATCH (s:Module {id: edge.source})-[r:DEPENDS_ON]->(t:Module {id: edge.target})\n        DELETE r\n        "
        self.transaction.run(merge_query, batch=batch_data)

    def _batch_add_contains_edges(self, mutations: list[Mutation]):
        batch_data = [
            m.model_dump() for m in mutations if isinstance(m, AddContainsEdgeMutation)
        ]
        if not batch_data:
            return
        merge_query = "\n        UNWIND $batch AS edge\n        MATCH (s:Module {id: edge.source}), (t:Module {id: edge.target})\n        MERGE (s)-[:CONTAINS]->(t)\n        "
        self.transaction.run(merge_query, batch=batch_data)

    def _batch_remove_contains_edges(self, mutations: list[Mutation]):
        batch_data = [
            m.model_dump()
            for m in mutations
            if isinstance(m, RemoveContainsEdgeMutation)
        ]
        if not batch_data:
            return
        merge_query = "\n        UNWIND $batch AS edge\n        MATCH (s:Module {id: edge.source})-[r:CONTAINS]->(t:Module {id: edge.target})\n        DELETE r\n        "
        self.transaction.run(merge_query, batch=batch_data)

    def _batch_handle_mutations(self, mutations: list[Mutation]):
        self._batch_add_depends_on_edges(mutations)
        self._batch_remove_depends_on_edges(mutations)
        self._batch_add_contains_edges(mutations)
        self._batch_remove_contains_edges(mutations)

    @override
    def update_fqn_prefix(self, old_fqn: ModuleFqn, new_fqn: ModuleFqn) -> None:
        query = '\n        MATCH (m:Module)\n        WHERE m.fqn STARTS WITH ($old_prefix + ".")\n        SET m.fqn = $new_prefix + substring(m.fqn, size($old_prefix))\n        '
        result = self.transaction.run(
            query, old_prefix=str(old_fqn), new_prefix=str(new_fqn)
        )
        result.consume()

    @override
    def find_by_fqn(self, fqn: ModuleFqn) -> Module | None:
        query = '\n        MATCH (m:Module {fqn: $fqn})\n        OPTIONAL MATCH (m)-[:DEPENDS_ON]->(target:Module)\n        OPTIONAL MATCH (m)-[:CONTAINS]->(child:Module)\n        RETURN \n            m, \n            "Package" IN labels(m) AS is_package,\n            collect(DISTINCT target.id) AS dependencies,\n            collect(DISTINCT child.id) AS contains\n        '
        result = self.transaction.run(query, fqn=str(fqn)).single()
        if not result:
            return None
        node = result["m"]
        dependencies = result["dependencies"]
        contains = result["contains"]
        module = Module.reconstitute(
            module_id=node["id"],
            fqn=node["fqn"],
            name=node["name"],
            is_package=result["is_package"],
            dependencies=dependencies,
            contains=contains,
        )
        self._seens.add(module)
        return module

    @override
    def get_dependencies(self, id: ModuleId) -> list[ModuleFqn]:
        query = '\n        MATCH (target:Module {id: $id})\n        OPTIONAL MATCH (target)-[:CONTAINS*1..]->(child:File)\n        WHERE "Package" IN labels(target)\n        WITH target, collect(DISTINCT child) + [target] AS internals\n        UNWIND internals AS internal\n        MATCH (caller:Module)-[:DEPENDS_ON]->(internal)\n        RETURN DISTINCT caller.fqn AS caller_fqn\n        '
        result = self.transaction.run(query, id=str(id))
        return [ModuleFqn(record["caller_fqn"]) for record in result]
