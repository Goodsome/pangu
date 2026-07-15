from abc import ABC, abstractmethod

from code_structure.application.dtos.symbol_dto import SymbolDto


class SymbolQuery(ABC):

    @abstractmethod
    def find_by_names(self, names: list[str]) -> list[SymbolDto]:
        ...