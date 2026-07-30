from abc import ABC
from d4_leaderboard.domain.repositories.entry_repository import EntryRepository
from abc import abstractmethod


class RepoProvider(ABC):
    @property
    @abstractmethod
    def entries(self) -> EntryRepository:
        pass
