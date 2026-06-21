from dataclasses import dataclass

from architecture.domain.aggregates.module import Module
from architecture.domain.identities.module_id import ModuleId
from architecture.domain.mutasions.add_contains_edge import AddContainsEdgeMutation
from architecture.domain.mutasions.add_depends_on_edge import AddDependsEdgeMutation
from architecture.domain.mutasions.remove_contains_edge import RemoveContainsEdgeMutation
from architecture.domain.mutasions.remove_depends_on_edge import RemoveDependsEdgeMutation
from architecture.domain.repositories.module_repository import ModuleRepository
from typing import override

from neo4j import Transaction

from codegen.shared.domain.core.mutation_collector import Mutation



@dataclass
class MemgraphModuleRepository(ModuleRepository):
    transaction: Transaction

    @override
    def _add(self, aggregate: Module) -> None:
        query = """
        CREATE (m:Module {
            id: $id,
            fqn: $fqn,
            name: $name,
            is_package: $is_package
        })
        """
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

        query = """
        UNWIND $modules AS mod
        CREATE (m:Module {
            id: mod.id,
            fqn: mod.fqn,
            name: mod.name,
            is_package: mod.is_package
        })
        """
        
        modules_data: list[dict[str, object]] = []
        mutations: list[Mutation] = []
        for agg in aggregates:
            modules_data.append(self._aggregate_to_dict(agg))
            mutations.extend(agg.collect_mutations())
            
        self.transaction.run(query, modules=modules_data)
        self._batch_handle_mutations(mutations)

    @override
    def _get(self, id: ModuleId) -> Module:
        query = """
        MATCH (m:Module {id: $id})
        OPTIONAL MATCH (m)-[:DEPENDS_ON]->(target:Module)
        OPTIONAL MATCH (m)-[:CONTAINS]->(child:Module)
        RETURN 
            m, 
            collect(DISTINCT target.id) AS dependencies,
            collect(DISTINCT child.id) AS contains
        """
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
            is_package=node["is_package"],
            dependencies=dependencies,
            contains=contains,
        )

        return module

    @override
    def _save(self, aggregate: Module) -> None:
        query = """
        MERGE (m:Module {id: $id})
        SET m.fqn = $fqn,
            m.name = $name,
            m.is_package = $is_package
        """
        self.transaction.run(
            query,
            id=str(aggregate.id),
            fqn=str(aggregate.fqn),
            name=aggregate.name,
            is_package=aggregate.is_package,
        )

        self._batch_handle_mutations(aggregate.collect_mutations())

    @override
    def _save_all(self, aggregates: list[Module]) -> None:
        if not aggregates:
            return

        query = """
        UNWIND $modules AS mod
        MERGE (m:Module {id: mod.id})
        SET m.fqn = mod.fqn,
            m.name = mod.name,
            m.is_package = mod.is_package
        """
        modules_data: list[dict[str, object]] = []
        mutations: list[Mutation] = []
        for agg in aggregates:
            modules_data.append(self._aggregate_to_dict(agg))
            mutations.extend(agg.collect_mutations())
            
        self.transaction.run(query, modules=modules_data)
        self._batch_handle_mutations(mutations)

    @override
    def _delete(self, aggregate: Module) -> None:
        query = """
        MATCH (m:Module {id: $id})
        DETACH DELETE m
        """
        self.transaction.run(query, id=str(aggregate.id))

    def _aggregate_to_dict(self, aggregate: Module) -> dict[str, object]:
        """辅助方法：将 Aggregate Root 序列化为 Cypher UNWIND 兼容的字典"""
        return {
            "id": str(aggregate.id),
            "fqn": str(aggregate.fqn),
            "name": aggregate.name,
            "is_package": aggregate.is_package,
        }

    def _batch_add_depends_on_edges(self, mutations: list[Mutation]):
        batch_data = [m.model_dump() for m in mutations if isinstance(m, AddDependsEdgeMutation)]
        if not batch_data:
            return
        merge_query = """
        UNWIND $batch AS edge
        MATCH (s:Module {id: edge.source}), (t:Module {id: edge.target})
        MERGE (s)-[:DEPENDS_ON]->(t)
        """
        self.transaction.run(merge_query, batch=batch_data)
        
    def _batch_remove_depends_on_edges(self, mutations: list[Mutation]):
        batch_data = [m.model_dump() for m in mutations if isinstance(m, RemoveDependsEdgeMutation)]
        if not batch_data:
            return
        merge_query = """
        UNWIND $batch AS edge
        MATCH (s:Module {id: edge.source})-[r:DEPENDS_ON]->(t:Module {id: edge.target})
        DELETE r
        """
        self.transaction.run(merge_query, batch=batch_data)

    def _batch_add_contains_edges(self, mutations: list[Mutation]):
        batch_data = [m.model_dump() for m in mutations if isinstance(m, AddContainsEdgeMutation)]
        if not batch_data:
            return
        merge_query = """
        UNWIND $batch AS edge
        MATCH (s:Module {id: edge.source}), (t:Module {id: edge.target})
        MERGE (s)-[:CONTAINS]->(t)
        """
        self.transaction.run(merge_query, batch=batch_data)

    def _batch_remove_contains_edges(self, mutations: list[Mutation]):
        batch_data = [m.model_dump() for m in mutations if isinstance(m, RemoveContainsEdgeMutation)]
        if not batch_data:
            return
        merge_query = """
        UNWIND $batch AS edge
        MATCH (s:Module {id: edge.source})-[r:CONTAINS]->(t:Module {id: edge.target})
        DELETE r
        """
        self.transaction.run(merge_query, batch=batch_data)

    def _batch_handle_mutations(self, mutations: list[Mutation]):
        self._batch_add_depends_on_edges(mutations)
        self._batch_remove_depends_on_edges(mutations)
        self._batch_add_contains_edges(mutations)
        self._batch_remove_contains_edges(mutations)
