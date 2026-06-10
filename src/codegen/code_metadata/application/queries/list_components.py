from dataclasses import dataclass
from codegen.code_metadata.application.dtos.component_dto import ComponentDto
from codegen.code_metadata.application.dtos.component_filter import ComponentFilter
from codegen.code_metadata.application.ports.component_query_service import (
    ComponentQueryService,
)
from codegen.shared.application.dtos.page import Page
from codegen.shared.application.dtos.page_query import PageQuery


@dataclass
class ListComponents:
    query_service: ComponentQueryService

    def execute(self, query: PageQuery[ComponentFilter]) -> Page[ComponentDto]:
        return self.query_service.find_page(query)
