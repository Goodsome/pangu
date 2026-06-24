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
        MATCH (target:Module {id: $id})
        WITH target,
             CASE 
               WHEN "Package" IN labels(target) THEN [(target)-[:CONTAINS*1..]->(child:File) | child]
               ELSE []
             END + target AS internals
        UNWIND internals AS internal
        MATCH (caller:Module)-[:DEPENDS_ON]->(internal)
        WHERE NOT caller IN internals
        RETURN DISTINCT caller.fqn AS caller_fqn
        """
        
        with self.driver.session() as session:
            def _read_tx(tx):
                result = tx.run(query, id=str(id))
                return [
                    ModuleFqn(record["caller_fqn"])
                    for record in result
                ]
                
            return session.execute_read(_read_tx)

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

    @override
    def find_empty_leaf_packages(self) -> list[ModuleFqn]:
        query = """
        MATCH (p:Package)
        WHERE NOT EXISTS {
            MATCH (p)-[:CONTAINS*0..]->(desc:Module)
            WHERE "File" IN labels(desc)
        }
        AND NOT EXISTS {
          MATCH (parent:Package)-[:CONTAINS]->(p)
          WHERE NOT EXISTS {
              MATCH (parent)-[:CONTAINS*0..]->(desc:Module)
              WHERE "File" IN labels(desc)
          }
        }
        RETURN p.fqn AS fqn
        """
        with self.driver.session() as session:
            def _read_tx(tx):
                result = tx.run(query)
                return [ModuleFqn(record["fqn"]) for record in result]
            return session.execute_read(_read_tx)

    @override
    def find_unused_modules(self) -> list[ModuleFqn]:
        query = """
        MATCH (m:Module:File)
        WHERE NOT EXISTS {
            MATCH (m)<-[:DEPENDS_ON]-()
        }
        AND m.name != "main"
        AND NOT m.fqn STARTS WITH "foundation"
        RETURN m.fqn AS fqn
        """
        with self.driver.session() as session:
            def _read_tx(tx):
                result = tx.run(query)
                return [ModuleFqn(record["fqn"]) for record in result]
            return session.execute_read(_read_tx)