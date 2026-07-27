from abc import ABC
from foundation.persistence.ports.base_unit_of_work import BaseUnitOfWork
from d4_leaderboard.domain.repositories.entry_repository import EntryRepository
from abc import abstractmethod


class UnitOfWork(BaseUnitOfWork, ABC):
    @property
    @abstractmethod
    def entries(self) -> EntryRepository:
        pass
