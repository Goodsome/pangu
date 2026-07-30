from dataclasses import dataclass
from code_structure.application.dtos.symbol_dto import SymbolDto
from code_structure.application.ports.symbol_query_service import SymbolQuery
from pydantic import BaseModel


class GetSymbolsQuery(BaseModel):
    names: list[str]


@dataclass
class GetSymbolsQueryHandler:
    symbol_query: SymbolQuery

    def execute(self, query: GetSymbolsQuery) -> list[SymbolDto]:
        return self.symbol_query.find_by_names(query.names)
