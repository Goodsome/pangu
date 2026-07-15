from dataclasses import dataclass
from code_structure.application.dtos.symbol_dto import SymbolDto
from code_structure.application.ports.symbol_query_service import SymbolQuery
from pydantic import BaseModel

class GetSymbolsQuery(BaseModel):
    names: list[str]


@dataclass
class GetSymbolsQueryHandler:
    query_service: SymbolQuery

    def execute(self, query: GetSymbolsQuery) -> list[SymbolDto]:
        return self.query_service.find_by_names(query.names)