from collections.abc import Iterator
from types import TracebackType
import logging
from abc import ABC
from abc import abstractmethod
from typing import Self
from foundation.building_blocks.event import DomainEvent, IntegrationEvent

logger = logging.getLogger(__name__)


class BaseUnitOfWork(ABC):
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

    @abstractmethod
    def collect_events(self) -> Iterator[DomainEvent]:
        pass
