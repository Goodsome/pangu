from foundation.persistence.ports.base_unit_of_work import BaseUnitOfWork
from abc import abstractmethod
from d4_leaderboard.domain.repositories.entry_repository import EntryRepository
from abc import ABC


class UnitOfWork(BaseUnitOfWork, ABC):
    @property
    @abstractmethod
    def entries(self) -> EntryRepository:
        pass
