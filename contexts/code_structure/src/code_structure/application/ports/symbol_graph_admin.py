from abc import ABC, abstractmethod


class SymbolGraphAdmin(ABC):

    @abstractmethod
    def purge_data(self) -> None:
        ...
        