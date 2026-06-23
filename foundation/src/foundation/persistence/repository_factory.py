from typing import Protocol, Any
from sqlalchemy.orm import Session
from foundation.persistence.repository import Repository


class RepositoryFactory[T: Repository[Any, Any]](Protocol):
    def __call__(self, session: Session) -> T: ...
