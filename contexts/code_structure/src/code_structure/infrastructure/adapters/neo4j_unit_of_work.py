from dataclasses import dataclass, field
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
    """code_structure Neo4j Unit of Work 实现。

    所有 repository 属性均使用懒加载缓存，确保同一 UoW 生命周期内
    返回同一实例，以保证 `_seens` 集合（领域事件收集）不丢失。
    """

    _file_modules: Neo4jFileModuleRepository | None = field(default=None, init=False)
    _classes: Neo4jClassRepository | None = field(default=None, init=False)
    _functions: Neo4jFunctionRepository | None = field(default=None, init=False)
    _variables: Neo4jVariableRepository | None = field(default=None, init=False)
    _external_symbols: Neo4jExternalSymbolRepository | None = field(
        default=None, init=False
    )
    _graph_admin: Neo4jSymbolGraphAdmin | None = field(default=None, init=False)
    _outbox: Neo4jOutboxRepository | None = field(default=None, init=False)

    @property
    @override
    def file_modules(self) -> FileModuleRepository:
        if self._file_modules is None:
            self._file_modules = Neo4jFileModuleRepository(session=self.session)
        return self._file_modules

    @property
    @override
    def classes(self) -> ClassRepository:
        if self._classes is None:
            self._classes = Neo4jClassRepository(session=self.session)
        return self._classes

    @property
    @override
    def functions(self) -> FunctionRepository:
        if self._functions is None:
            self._functions = Neo4jFunctionRepository(session=self.session)
        return self._functions

    @property
    @override
    def variables(self) -> VariableRepository:
        if self._variables is None:
            self._variables = Neo4jVariableRepository(session=self.session)
        return self._variables

    @property
    @override
    def external_symbols(self) -> ExternalSymbolRepository:
        if self._external_symbols is None:
            self._external_symbols = Neo4jExternalSymbolRepository(session=self.session)
        return self._external_symbols

    @property
    @override
    def graph_admin(self) -> SymbolGraphAdmin:
        if self._graph_admin is None:
            self._graph_admin = Neo4jSymbolGraphAdmin(session=self.session)
        return self._graph_admin

    @property
    @override
    def outbox(self) -> OutboxRepository:
        if self._outbox is None:
            self._outbox = Neo4jOutboxRepository(session=self.session)
        return self._outbox
