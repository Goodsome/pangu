from collections.abc import Collection
from dataclasses import dataclass
from typing import assert_never, override
from architecture.infrastructure.mappers.module_to_module_node import (
    module_to_module_node,
)
from architecture.infrastructure.orm_models.module_node import (
    ContainsEdge,
    DependsOnEdge,
)
from foundation.building_blocks.mutation_collector import Mutation
from foundation.common_types.fqns.fqn import ModuleFqn
from foundation.common_types.identities.module_id import ModuleId
from foundation.persistence.sessions.neo4j_session import Neo4jSession
from architecture.domain.aggregates.module import Module
from architecture.domain.mutations.add_contains_edge import AddContainsEdgeMutation
from architecture.domain.mutations.add_depends_on_edge import AddDependsEdgeMutation
from architecture.domain.mutations.remove_contains_edge import (
    RemoveContainsEdgeMutation,
)
from architecture.domain.mutations.remove_depends_on_edge import (
    RemoveDependsEdgeMutation,
)
from architecture.domain.repositories.module_repository import ModuleRepository


@dataclass
class Neo4jModuleRepository(ModuleRepository):
    session: Neo4jSession

    @override
    def _add(self, aggregate: Module) -> None:
        module_node = module_to_module_node(aggregate)
        self.session.save_node(module_node)
        self._batch_handle_mutations(aggregate.collect_mutations())

    @override
    def _add_all(self, aggregates: list[Module]) -> None:
        for agg in aggregates:
            self._add(agg)

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
        module_node = module_to_module_node(aggregate)
        self.session.save_node(module_node)
        self._batch_handle_mutations(aggregate.collect_mutations())

    @override
    def _save_all(self, aggregates: list[Module]) -> None:
        for agg in aggregates:
            self._save(agg)

    @override
    def _delete(self, aggregate: Module) -> None:
        self.session.delete_node(node_id=str(aggregate.id))

    @override
    def delete_all(self, ids: list[ModuleId]) -> None:
        for id in ids:
            self.session.delete_node(node_id=str(id))


    def _batch_handle_mutations(self, mutations: list[Mutation]):
        for mutation in mutations:
            match mutation:
                case AddDependsEdgeMutation():
                    edge = DependsOnEdge(
                        source_id=str(mutation.source), target_id=str(mutation.target)
                    )
                    self.session.save_edge(edge)
                case RemoveDependsEdgeMutation():
                    edge = DependsOnEdge(
                        source_id=str(mutation.source), target_id=str(mutation.target)
                    )
                    self.session.delete_edge(edge)
                case AddContainsEdgeMutation():
                    edge = ContainsEdge(
                        source_id=str(mutation.source), target_id=str(mutation.target)
                    )
                    self.session.save_edge(edge)
                case RemoveContainsEdgeMutation():
                    edge = ContainsEdge(
                        source_id=str(mutation.source), target_id=str(mutation.target)
                    )
                    self.session.delete_edge(edge)
                case Mutation():
                    raise NotImplementedError
                case _:
                    assert_never(mutation)

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
