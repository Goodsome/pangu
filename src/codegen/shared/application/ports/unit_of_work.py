from types import TracebackType
import logging
from abc import ABC
from abc import abstractmethod
from typing import Self
from typing import Any
from codegen.shared.domain.core.event import IntegrationEvent
from codegen.shared.domain.ports.repository import Repository

logger = logging.getLogger(__name__)


class UnitOfWork[T_Repo: Repository[Any, Any]](ABC):

    @property
    @abstractmethod
    def repository(self) -> T_Repo:
        pass

    @abstractmethod
    def __enter__(self) -> Self:
        pass

    @abstractmethod
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass

    @abstractmethod
    def save_outbox_message(self, message: IntegrationEvent):
        pass