from dataclasses import dataclass

from code_structure.application.dtos.symbol_dto import SymbolDto
from code_structure.application.queries.get_symbols import (
    GetSymbolsQuery,
    GetSymbolsQueryHandler,
)


@dataclass
class CodeStructureApi:
    get_symbols_query_handler: GetSymbolsQueryHandler

    def get_symbols(self, names: list[str]) -> list[SymbolDto]:
        query = GetSymbolsQuery(names=names)
        return self.get_symbols_query_handler.execute(query)
