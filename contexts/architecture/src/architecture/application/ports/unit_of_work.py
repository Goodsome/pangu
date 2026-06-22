from architecture.infrastructure.repositories.neo4j_module_repository import Neo4jModuleRepository
from codegen.shared.application.ports.unit_of_work import UnitOfWork as BaseUnitOfWork

UnitOfWork = BaseUnitOfWork[Neo4jModuleRepository]
