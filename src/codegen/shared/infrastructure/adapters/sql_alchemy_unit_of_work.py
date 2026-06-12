import logging
from dataclasses import dataclass
from dataclasses import field
from types import TracebackType
from typing import Any
from typing import Callable
from typing import override
from typing import Self
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from codegen.shared.application.ports.unit_of_work import UnitOfWork
from codegen.shared.domain.ports.repository import Repository

logger = logging.getLogger(__name__)


@dataclass
class SqlAlchemyUnitOfWork[T_Repo: Repository[Any, Any]](UnitOfWork[T_Repo]):
    session_factory: sessionmaker[Session]
    repository_factory: Callable[[Session], T_Repo]
    session: Session | None = field(default=None, init=False)
    _repository: T_Repo | None = field(default=None, init=False)

    @override
    def __enter__(self) -> Self:
        self.session = self.session_factory()
        self._repository = self.repository_factory(self.session)
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
            logger.error(f"Transaction rolled back due to error: {exc_val}")
        else:
            pass
        if self.session:
            self.session.close()
            self.session = None
            self._repository = None

    @property
    @override
    def repository(self) -> T_Repo:
        if not self._repository:
            raise RuntimeError("Unit of work is not active. Use 'with uow:' block.")
        return self._repository

    @override
    def commit(self):
        if self.session:
            self.session.commit()

    @override
    def rollback(self):
        if self.session:
            self.session.rollback()
