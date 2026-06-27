from collections.abc import Collection
from dataclasses import dataclass
from typing import override

from foundation.building_blocks.mutation_collector import Mutation
from foundation.common_types.fqns.fqn import ModuleFqn
from foundation.common_types.identities.module_id import ModuleId
from foundation.persistence.sessions.neo4j_session import Neo4jSession

from architecture.domain.aggregates.module import Module
from architecture.domain.mutasions.add_contains_edge import AddContainsEdgeMutation
from architecture.domain.mutasions.add_depends_on_edge import AddDependsEdgeMutation
from architecture.domain.mutasions.remove_contains_edge import (
    RemoveContainsEdgeMutation,
)
from architecture.domain.mutasions.remove_depends_on_edge import (
    RemoveDependsEdgeMutation,
)
from architecture.domain.repositories.module_repository import ModuleRepository


@dataclass
class Neo4jModuleRepository(ModuleRepository):
    session: Neo4jSession

    @override
    def _add(self, aggregate: Module) -> None:
        query = " CREATE (m {     id: $id,     fqn: $fqn,     name: $name }) WITH m CALL {     WITH m, $is_package AS is_pkg     WHERE is_pkg     SET m:Package } CALL {     WITH m, $is_package AS is_pkg     WHERE NOT is_pkg     SET m:File } "
        self.session.execute(
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
        query = " UNWIND $modules AS mod CREATE (m:Module {     id: mod.id,     fqn: mod.fqn,     name: mod.name }) FOREACH (_ IN CASE WHEN mod.is_package THEN [1] ELSE [] END |     SET m:Package ) FOREACH (_ IN CASE WHEN NOT mod.is_package THEN [1] ELSE [] END |     SET m:File ) "
        modules_data: list[dict[str, object]] = []
        mutations: list[Mutation] = []
        for agg in aggregates:
            modules_data.append(self._aggregate_to_dict(agg))
            mutations.extend(agg.collect_mutations())
        self.session.execute(query, modules=modules_data)
        self._batch_handle_mutations(mutations)

    @override
    def _get(self, id: ModuleId) -> Module:
        query = ' MATCH (m:Module {id: $id}) OPTIONAL MATCH (m)-[:DEPENDS_ON]->(target:Module) OPTIONAL MATCH (m)-[:CONTAINS]->(child:Module) RETURN     m,     "Package" IN labels(m) AS is_package,     collect(DISTINCT target.id) AS dependencies,     collect(DISTINCT child.id) AS contains '
        result = self.session.execute(query, id=str(id)).single()
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
        query = " MERGE (m:Module {id: $id}) SET m.fqn = $fqn,     m.name = $name "
        self.session.execute(
            query, id=str(aggregate.id), fqn=str(aggregate.fqn), name=aggregate.name
        )
        self._batch_handle_mutations(aggregate.collect_mutations())

    @override
    def _save_all(self, aggregates: list[Module]) -> None:
        if not aggregates:
            return
        query = " UNWIND $modules AS mod MERGE (m:Module {id: mod.id}) SET m.fqn = mod.fqn,     m.name = mod.name "
        modules_data: list[dict[str, object]] = []
        mutations: list[Mutation] = []
        for agg in aggregates:
            modules_data.append(self._aggregate_to_dict(agg))
            mutations.extend(agg.collect_mutations())
        self.session.execute(query, modules=modules_data)
        self._batch_handle_mutations(mutations)

    @override
    def _delete(self, aggregate: Module) -> None:
        query = " MATCH (m:Module {id: $id}) DETACH DELETE m "
        self.session.execute(query, id=str(aggregate.id))

    @override
    def delete_all(self, ids: list[ModuleId]) -> None:
        if not ids:
            return
        query = " UNWIND $batch_ids AS mod_id MATCH (m:Module {id: mod_id}) DETACH DELETE m "
        self.session.execute(query, batch_ids=[str(id) for id in ids])

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
        query = " UNWIND $batch AS edge MATCH (s:Module {id: edge.source}), (t:Module {id: edge.target}) MERGE (s)-[:DEPENDS_ON]->(t) "
        self.session.execute(query, batch=batch_data)

    def _batch_remove_depends_on_edges(self, mutations: list[Mutation]):
        batch_data = [
            m.model_dump()
            for m in mutations
            if isinstance(m, RemoveDependsEdgeMutation)
        ]
        if not batch_data:
            return
        query = " UNWIND $batch AS edge MATCH (s:Module {id: edge.source})-[r:DEPENDS_ON]->(t:Module {id: edge.target}) DELETE r "
        self.session.execute(query, batch=batch_data)

    def _batch_add_contains_edges(self, mutations: list[Mutation]):
        batch_data = [
            m.model_dump() for m in mutations if isinstance(m, AddContainsEdgeMutation)
        ]
        if not batch_data:
            return
        query = " UNWIND $batch AS edge MATCH (s:Module {id: edge.source}), (t:Module {id: edge.target}) MERGE (s)-[:CONTAINS]->(t) "
        self.session.execute(query, batch=batch_data)

    def _batch_remove_contains_edges(self, mutations: list[Mutation]):
        batch_data = [
            m.model_dump()
            for m in mutations
            if isinstance(m, RemoveContainsEdgeMutation)
        ]
        if not batch_data:
            return
        query = " UNWIND $batch AS edge MATCH (s:Module {id: edge.source})-[r:CONTAINS]->(t:Module {id: edge.target}) DELETE r "
        self.session.execute(query, batch=batch_data)

    def _batch_handle_mutations(self, mutations: list[Mutation]):
        self._batch_add_depends_on_edges(mutations)
        self._batch_remove_depends_on_edges(mutations)
        self._batch_add_contains_edges(mutations)
        self._batch_remove_contains_edges(mutations)

    @override
    def update_fqn_prefix(self, old_fqn: ModuleFqn, new_fqn: ModuleFqn) -> None:
        query = ' MATCH (m:Module) WHERE m.fqn STARTS WITH ($old_prefix + ".") SET m.fqn = $new_prefix + substring(m.fqn, size($old_prefix)) '
        result = self.session.execute(
            query, old_prefix=str(old_fqn), new_prefix=str(new_fqn)
        )
        result.consume()

    @override
    def find_by_fqn(self, fqn: ModuleFqn) -> Module | None:
        query = ' MATCH (m:Module {fqn: $fqn}) OPTIONAL MATCH (m)-[:DEPENDS_ON]->(target:Module) OPTIONAL MATCH (m)-[:CONTAINS]->(child:Module) RETURN     m,     "Package" IN labels(m) AS is_package,     collect(DISTINCT target.id) AS dependencies,     collect(DISTINCT child.id) AS contains '
        result = self.session.execute(query, fqn=str(fqn)).single()
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
    def find_by_fqns(self, fqns: Collection[ModuleFqn]) -> list[Module]:
        if not fqns:
            return []
        query = ' MATCH (m:Module) WHERE m.fqn IN $fqns OPTIONAL MATCH (m)-[:DEPENDS_ON]->(target:Module) OPTIONAL MATCH (m)-[:CONTAINS]->(child:Module) RETURN     m,     "Package" IN labels(m) AS is_package,     collect(DISTINCT target.id) AS dependencies,     collect(DISTINCT child.id) AS contains '
        results = self.session.execute(query, fqns=[str(f) for f in fqns])
        modules: list[Module] = []
        for record in results:
            node = record["m"]
            module = Module.reconstitute(
                module_id=node["id"],
                fqn=node["fqn"],
                name=node["name"],
                is_package=record["is_package"],
                dependencies=record["dependencies"],
                contains=record["contains"],
            )
            modules.append(module)
            self._seens.add(module)
        return modules

    @override
    def get_dependencies(self, id: ModuleId) -> list[ModuleFqn]:
        query = ' MATCH (target:Module {id: $id}) OPTIONAL MATCH (target)-[:CONTAINS*1..]->(child) WHERE "Package" IN labels(target) WITH target, collect(DISTINCT child) + [target] AS internals UNWIND internals AS internal MATCH (caller:Module:File)-[:DEPENDS_ON]->(internal) RETURN DISTINCT caller.fqn AS caller_fqn '
        result = self.session.execute(query, id=str(id))
        return [ModuleFqn(record["caller_fqn"]) for record in result]
