from abc import ABC, abstractmethod
from d4_leaderboard.domain.repositories.entry_repository import EntryRepository


class RepoProvider(ABC):
    @property
    @abstractmethod
    def entries(self) -> EntryRepository:
        pass
