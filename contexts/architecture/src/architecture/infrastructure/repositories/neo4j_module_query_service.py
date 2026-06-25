from dataclasses import dataclass
from typing import override
from neo4j import Driver
from architecture.application.ports.module_query_serivce import ModuleQueryService
from foundation.common_types.identities.module_id import ModuleId
from foundation.common_types.fqns.fqn import ModuleFqn


@dataclass
class Neo4jModuleQueryService(ModuleQueryService):
    driver: Driver

    @override
    def get_external_dependencies(self, id: ModuleId) -> list[ModuleFqn]:
        query = '\n        MATCH (target:Module {id: $id})\n        WITH target,\n             CASE \n               WHEN "Package" IN labels(target) THEN [(target)-[:CONTAINS*1..]->(child:File) | child]\n               ELSE []\n             END + target AS internals\n        UNWIND internals AS internal\n        MATCH (caller:Module)-[:DEPENDS_ON]->(internal)\n        WHERE NOT caller IN internals\n        RETURN DISTINCT caller.fqn AS caller_fqn\n        '
        with self.driver.session() as session:

            def _read_tx(tx):
                result = tx.run(query, id=str(id))
                return [ModuleFqn(record["caller_fqn"]) for record in result]

            return session.execute_read(_read_tx)

    @override
    def get_child_ids(self, id: ModuleId) -> list[ModuleId]:
        query = "\n        MATCH (m:Module {id: $id})-[:CONTAINS]->(child:Module)\n        RETURN collect(child.id) AS child_ids\n        "
        with self.driver.session() as session:
            result = session.run(query, id=str(id)).single()
            if not result:
                return []
            return [ModuleId.reconstitute(cid) for cid in result["child_ids"]]

    @override
    def get_descendant_ids(self, id: ModuleId) -> list[ModuleId]:
        query = "\n        MATCH (m:Module {id: $id})-[:CONTAINS*1..]->(descendant:Module)\n        RETURN DISTINCT descendant.id AS descendant_id\n        "
        with self.driver.session() as session:

            def _read_tx(tx):
                result = tx.run(query, id=str(id))
                return [record["descendant_id"] for record in result]

            descendant_s_strings = session.execute_read(_read_tx)
            return [ModuleId.reconstitute(did) for did in descendant_s_strings]

    @override
    def find_empty_leaf_packages(self) -> list[ModuleFqn]:
        query = '\n        MATCH (p:Package)\n        WHERE NOT EXISTS {\n            MATCH (p)-[:CONTAINS*0..]->(desc:Module)\n            WHERE "File" IN labels(desc)\n        }\n        AND NOT EXISTS {\n          MATCH (parent:Package)-[:CONTAINS]->(p)\n          WHERE NOT EXISTS {\n              MATCH (parent)-[:CONTAINS*0..]->(desc:Module)\n              WHERE "File" IN labels(desc)\n          }\n        }\n        RETURN p.fqn AS fqn\n        '
        with self.driver.session() as session:

            def _read_tx(tx):
                result = tx.run(query)
                return [ModuleFqn(record["fqn"]) for record in result]

            return session.execute_read(_read_tx)

    @override
    def find_unused_modules(self) -> list[ModuleFqn]:
        query = '\n        MATCH (m:Module:File)\n        WHERE NOT EXISTS {\n            MATCH (m)<-[:DEPENDS_ON]-()\n        }\n        AND m.name != "main"\n        AND NOT m.fqn STARTS WITH "foundation"\n        RETURN m.fqn AS fqn\n        '
        with self.driver.session() as session:

            def _read_tx(tx):
                result = tx.run(query)
                return [ModuleFqn(record["fqn"]) for record in result]

            return session.execute_read(_read_tx)
