from dataclasses import dataclass
from pydantic import BaseModel

from code_structure.application.dtos.symbol_dto import SymbolDto
from code_structure.application.ports.symbol_query_service import SymbolQuery


class GetAggregatesQuery(BaseModel):
    context: str


@dataclass
class GetAggregatesQueryHandler:
    symbol_query: SymbolQuery

    def execute(self, query: GetAggregatesQuery) -> list[SymbolDto]:
        return self.symbol_query.find_aggregates_by_context(query.context)
