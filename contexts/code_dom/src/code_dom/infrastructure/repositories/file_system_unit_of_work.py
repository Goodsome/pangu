import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import override
from code_dom.application.ports.repo_provider import RepoProvider
from code_dom.domain.repositories.codebase_repository import CodebaseRepository
from code_dom.domain.repositories.document_repository import DocumentRepository
from foundation.persistence.ports.session_manager import SessionManager
from foundation.persistence.sessions.file_system_session import FileSystemSession

logger = logging.getLogger(__name__)


@dataclass(kw_only=True)
class FileSystemUnitOfWork(SessionManager[FileSystemSession], RepoProvider):
    codebase_repository: CodebaseRepository
    document_repository: DocumentRepository

    @property
    @override
    def codebases(self) -> CodebaseRepository:
        return self.codebase_repository

    @property
    @override
    def documents(self) -> DocumentRepository:
        return self.document_repository
