from dataclasses import dataclass
from typing import override

from neo4j import Driver

from architecture.application.ports.module_query_serivce import ModuleQueryService
from architecture.domain.identities.module_id import ModuleId
from architecture.domain.value_objects.fqn import ModuleFqn


@dataclass
class Neo4jModuleQueryService(ModuleQueryService):
    driver: Driver

    @override
    def get_external_dependencies(self, id: ModuleId) -> list[ModuleFqn]:
        query = """
        MATCH (pkg:Module {id: $id})
        MATCH (pkg)-[:CONTAINS*1..]->(internal:Module)
        MATCH (caller:Module)-[:DEPENDS_ON]->(internal)
        WHERE NOT (pkg)-[:CONTAINS*1..]->(caller) AND caller <> pkg
        RETURN internal.fqn AS internal_module, collect(DISTINCT caller.fqn) AS external_callers
        """
        with self.driver.session() as session:
            result = session.run(query, id=str(id)).single()
            if not result:
                return []
            return [ModuleFqn(fqn) for fqn in result["callers"]]

    @override
    def get_child_ids(self, id: ModuleId) -> list[ModuleId]:
        query = """
        MATCH (m:Module {id: $id})-[:CONTAINS]->(child:Module)
        RETURN collect(child.id) AS child_ids
        """
        with self.driver.session() as session:
            result = session.run(query, id=str(id)).single()
            if not result:
                return []
            return [ModuleId.reconstitute(cid) for cid in result["child_ids"]]

    
    @override
    def get_descendant_ids(self, id: ModuleId) -> list[ModuleId]:
        query = """
        MATCH (m:Module {id: $id})-[:CONTAINS*1..]->(descendant:Module)
        RETURN DISTINCT descendant.id AS descendant_id
        """
        with self.driver.session() as session:
            def _read_tx(tx):
                result = tx.run(query, id=str(id))
                return [record["descendant_id"] for record in result]
                
            descendant_s_strings = session.execute_read(_read_tx)
            return [ModuleId.reconstitute(did) for did in descendant_s_strings]