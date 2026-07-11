from collections.abc import Collection
from dataclasses import dataclass
from typing import override
from architecture.infrastructure.mappers.module_to_module_node import (
    package_module_to_node,
)
from foundation.common_types.fqns.fqn import ModuleFqn
from foundation.common_types.identities.module_id import ModuleId
from foundation.persistence.sessions.neo4j_session import Neo4jSession
from architecture.domain.aggregates.package_module import PackageModule
from architecture.domain.repositories.package_module_repository import (
    PackageModuleRepository,
)


@dataclass
class Neo4jPackageModuleRepository(PackageModuleRepository):
    session: Neo4jSession

    @override
    def _add(self, aggregate: PackageModule) -> None:
        node = package_module_to_node(aggregate)
        self.session.save_node(node)

    @override
    def _add_all(self, aggregates: list[PackageModule]) -> None:
        for agg in aggregates:
            self._add(agg)

    @override
    def _get(self, id: ModuleId) -> PackageModule:
        query = (
            ' MATCH (m:Package {id: $id})'
            " OPTIONAL MATCH (m)-[:DEPENDS_ON]->(target:Module)"
            " OPTIONAL MATCH (m)-[:CONTAINS]->(child:Module)"
            " RETURN m, collect(DISTINCT target.id) AS dependencies,"
            " collect(DISTINCT child.id) AS contains"
        )
        result = self.session.execute(query, id=str(id)).single()
        if not result:
            raise ValueError(f"PackageModule with id {id} not found")
        node = result["m"]
        dependencies = result["dependencies"]
        contains = result["contains"]
        return PackageModule.reconstitute(
            module_id=node["id"],
            fqn=node["fqn"],
            name=node["name"],
            dependencies=dependencies,
            contains=contains,
        )

    @override
    def _save(self, aggregate: PackageModule) -> None:
        node = package_module_to_node(aggregate)
        self.session.save_node(node)

    @override
    def _save_all(self, aggregates: list[PackageModule]) -> None:
        for agg in aggregates:
            self._save(agg)

    @override
    def _delete(self, aggregate: PackageModule) -> None:
        self.session.delete_node(node_id=str(aggregate.id))

    @override
    def delete_all(self, ids: list[ModuleId]) -> None:
        for id in ids:
            self.session.delete_node(node_id=str(id))

    @override
    def update_fqn_prefix(self, old_fqn: ModuleFqn, new_fqn: ModuleFqn) -> None:
        query = (
            " MATCH (m:Package)"
            " WHERE m.fqn STARTS WITH ($old_prefix + '.')"
            " SET m.fqn = $new_prefix + substring(m.fqn, size($old_prefix))"
        )
        result = self.session.execute(
            query, old_prefix=str(old_fqn), new_prefix=str(new_fqn)
        )
        result.consume()

    @override
    def find_by_fqn(self, fqn: ModuleFqn) -> PackageModule | None:
        query = (
            ' MATCH (m:Package {fqn: $fqn})'
            " OPTIONAL MATCH (m)-[:DEPENDS_ON]->(target:Module)"
            " OPTIONAL MATCH (m)-[:CONTAINS]->(child:Module)"
            " RETURN m, collect(DISTINCT target.id) AS dependencies,"
            " collect(DISTINCT child.id) AS contains"
        )
        result = self.session.execute(query, fqn=str(fqn)).single()
        if not result:
            return None
        node = result["m"]
        dependencies = result["dependencies"]
        contains = result["contains"]
        module = PackageModule.reconstitute(
            module_id=node["id"],
            fqn=node["fqn"],
            name=node["name"],
            dependencies=dependencies,
            contains=contains,
        )
        self._seens.add(module)
        return module

    @override
    def find_by_fqns(self, fqns: Collection[ModuleFqn]) -> list[PackageModule]:
        if not fqns:
            return []
        query = (
            " MATCH (m:Package)"
            " WHERE m.fqn IN $fqns"
            " OPTIONAL MATCH (m)-[:DEPENDS_ON]->(target:Module)"
            " OPTIONAL MATCH (m)-[:CONTAINS]->(child:Module)"
            " RETURN m, collect(DISTINCT target.id) AS dependencies,"
            " collect(DISTINCT child.id) AS contains"
        )
        results = self.session.execute(query, fqns=[str(f) for f in fqns])
        modules: list[PackageModule] = []
        for record in results:
            node = record["m"]
            module = PackageModule.reconstitute(
                module_id=node["id"],
                fqn=node["fqn"],
                name=node["name"],
                dependencies=record["dependencies"],
                contains=record["contains"],
            )
            modules.append(module)
            self._seens.add(module)
        return modules

    @override
    def find_containing(self, child_fqn: ModuleFqn) -> PackageModule | None:
        query = (
            " MATCH (parent:Package)-[:CONTAINS]->(child:Module {fqn: $child_fqn})"
            " OPTIONAL MATCH (parent)-[:DEPENDS_ON]->(target:Module)"
            " OPTIONAL MATCH (parent)-[:CONTAINS]->(c:Module)"
            " RETURN parent, collect(DISTINCT target.id) AS dependencies,"
            " collect(DISTINCT c.id) AS contains"
        )
        result = self.session.execute(query, child_fqn=str(child_fqn)).single()
        if not result:
            return None
        node = result["parent"]
        module = PackageModule.reconstitute(
            module_id=node["id"],
            fqn=node["fqn"],
            name=node["name"],
            dependencies=result["dependencies"],
            contains=result["contains"],
        )
        self._seens.add(module)
        return module
