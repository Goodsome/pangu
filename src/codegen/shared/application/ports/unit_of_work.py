from collections.abc import Iterator
import logging
from abc import ABC
from abc import abstractmethod
from typing import Any, override
from codegen.shared.application.ports.base_unit_of_work import BaseUnitOfWork
from codegen.shared.domain.core.event import DomainEvent
from codegen.shared.domain.ports.repository import Repository

logger = logging.getLogger(__name__)


class UnitOfWork[T_Repo: Repository[Any, Any]](BaseUnitOfWork, ABC):

    @property
    @abstractmethod
    def repository(self) -> T_Repo:
        pass

    @override
    def collect_events(self) -> Iterator[DomainEvent]:
        return self.repository.collect_events()