from dataclasses import dataclass
from typing import override
from code_structure.application.ports.repo_provider import RepoProvider
from code_structure.application.ports.symbol_graph_admin import SymbolGraphAdmin
from code_structure.domain.repositories.class_repository import ClassRepository
from code_structure.domain.repositories.external_symbol_repository import (
    ExternalSymbolRepository,
)
from code_structure.domain.repositories.file_module_repository import (
    FileModuleRepository,
)
from code_structure.domain.repositories.function_repository import FunctionRepository
from code_structure.domain.repositories.variable_repository import VariableRepository
from code_structure.infrastructure.repositories.neo4j_class_repository import (
    Neo4jClassRepository,
)
from code_structure.infrastructure.repositories.neo4j_external_symbol_repository import (
    Neo4jExternalSymbolRepository,
)
from code_structure.infrastructure.repositories.neo4j_file_module_repository import (
    Neo4jFileModuleRepository,
)
from code_structure.infrastructure.repositories.neo4j_function_repository import (
    Neo4jFunctionRepository,
)
from code_structure.infrastructure.repositories.neo4j_symbol_graph_admin import (
    Neo4jSymbolGraphAdmin,
)
from code_structure.infrastructure.repositories.neo4j_variable_repository import (
    Neo4jVariableRepository,
)
from foundation.persistence.ports.outbox_repository import OutboxRepository
from foundation.persistence.ports.session_manager import SessionManager
from foundation.persistence.repositories.neo4j_outbox_repository import (
    Neo4jOutboxRepository,
)
from foundation.persistence.sessions.neo4j_session import Neo4jSession


@dataclass
class Neo4jUnitOfWork(SessionManager[Neo4jSession], RepoProvider):
    @property
    @override
    def file_modules(self) -> FileModuleRepository:
        return Neo4jFileModuleRepository(session=self.session)

    @property
    @override
    def classes(self) -> ClassRepository:
        return Neo4jClassRepository(session=self.session)

    @property
    @override
    def functions(self) -> FunctionRepository:
        return Neo4jFunctionRepository(session=self.session)

    @property
    @override
    def variables(self) -> VariableRepository:
        return Neo4jVariableRepository(session=self.session)

    @property
    @override
    def external_symbols(self) -> ExternalSymbolRepository:
        return Neo4jExternalSymbolRepository(session=self.session)

    @property
    @override
    def graph_admin(self) -> SymbolGraphAdmin:
        return Neo4jSymbolGraphAdmin(session=self.session)

    @property
    @override
    def outbox(self) -> OutboxRepository:
        return Neo4jOutboxRepository(session=self.session)
