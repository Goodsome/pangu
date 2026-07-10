from abc import ABC, abstractmethod


class GraphAdmin(ABC):
    @abstractmethod
    def purge_data(self) -> None: ...
