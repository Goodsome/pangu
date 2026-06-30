from dataclasses import dataclass, field
from types import TracebackType
from typing import Self, override
from code_structure.application.ports.symbol_graph_admin import SymbolGraphAdmin
from code_structure.application.ports.unit_of_work import UnitOfWork
from code_structure.domain.repositories.class_repository import ClassRepository
from code_structure.domain.repositories.file_module_repository import FileModuleRepository
from code_structure.domain.repositories.function_repository import FunctionRepository
from code_structure.domain.repositories.variable_repository import VariableRepository
from code_structure.infrastructure.repositories.neo4j_class_repository import Neo4jClassRepository
from code_structure.infrastructure.repositories.neo4j_file_module_repository import Neo4jFileModuleRepository
from code_structure.infrastructure.repositories.neo4j_function_repository import Neo4jFunctionRepository
from code_structure.infrastructure.repositories.neo4j_symbol_graph_admin import Neo4jSymbolGraphAdmin
from code_structure.infrastructure.repositories.neo4j_variable_repository import Neo4jVariableRepository
from foundation.building_blocks.event import IntegrationEvent
from foundation.persistence.sessions.neo4j_session import Neo4jSession
from neo4j import Driver


@dataclass
class Neo4jUnitOfWork(UnitOfWork):
    driver: Driver
    _session: Neo4jSession | None = field(default=None, init=False)
    _file_module_repo: Neo4jFileModuleRepository | None = field(default=None, init=False)
    _class_repo: Neo4jClassRepository | None = field(default=None, init=False)
    _function_repo: Neo4jFunctionRepository | None = field(default=None, init=False)
    _variable_repo: Neo4jVariableRepository | None = field(default=None, init=False)
    _graph_admin: Neo4jSymbolGraphAdmin | None = field(default=None, init=False)

    @override
    def __enter__(self) -> Self:
        self._session = Neo4jSession(driver=self.driver)
        self._file_module_repo = Neo4jFileModuleRepository(session=self._session)
        self._class_repo = Neo4jClassRepository(session=self._session)
        self._function_repo = Neo4jFunctionRepository(session=self._session)
        self._variable_repo = Neo4jVariableRepository(session=self._session)
        self._graph_admin = Neo4jSymbolGraphAdmin(session=self._session)
        return self

    @override
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        if exc_type is not None:
            self.rollback()
        if self._session:
            self._session.close()
            self._session = None
        self._file_module_repo = None
        self._class_repo = None
        self._function_repo = None
        self._variable_repo = None
        self._graph_admin = None

    @property
    @override
    def file_modules(self) -> FileModuleRepository:
        if not self._file_module_repo:
            raise RuntimeError("Unit of work is not active. Use 'with uow:' block.")
        return self._file_module_repo

    @property
    @override
    def classes(self) -> ClassRepository:
        if not self._class_repo:
            raise RuntimeError("Unit of work is not active. Use 'with uow:' block.")
        return self._class_repo

    @property
    @override
    def functions(self) -> FunctionRepository:
        if not self._function_repo:
            raise RuntimeError("Unit of work is not active. Use 'with uow:' block.")
        return self._function_repo

    @property
    @override
    def variables(self) -> VariableRepository:
        if not self._variable_repo:
            raise RuntimeError("Unit of work is not active. Use 'with uow:' block.")
        return self._variable_repo

    @property
    @override
    def graph_admin(self) -> SymbolGraphAdmin:
        if not self._graph_admin:
            raise RuntimeError("Unit of work is not active. Use 'with uow:' block.")
        return self._graph_admin

    @override
    def commit(self):
        if self._session:
            self._session.commit()

    @override
    def rollback(self):
        if self._session:
            self._session.rollback()

    @override
    def save_outbox_message(self, message: IntegrationEvent):
        if not self._session:
            raise RuntimeError("Transaction is not active")
        payload = message.model_dump(mode="json")
        event_type = type(message).__name__
        query = "CREATE (o:OutboxMessage { event_type: $event_type, payload: $payload, created_at: timestamp() })"
        self._session.execute(query, event_type=event_type, payload=payload)
