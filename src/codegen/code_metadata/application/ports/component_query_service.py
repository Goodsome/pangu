from abc import ABC
from abc import abstractmethod
from collections.abc import Collection
from codegen.code_metadata.application.dtos.component_dto import ComponentDto
from codegen.code_metadata.application.dtos.component_filter import ComponentFilter
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.shared.application.dtos.page import Page
from codegen.shared.application.dtos.page_query import PageQuery


class ComponentQueryService(ABC):

    @abstractmethod
    def find_by_name(self, name: str, context: str) -> ComponentDto | None:
        pass

    @abstractmethod
    def find_page(self, query: PageQuery[ComponentFilter]) -> Page[ComponentDto]:
        pass

    @abstractmethod
    def find_by_context_names(
        self, context_names: set[tuple[str, str]]
    ) -> list[ComponentDto]:
        pass

    @abstractmethod
    def find_by_ids(
        self, ids: Collection[ComponentId]
    ) -> dict[ComponentId, ComponentDto]:
        pass
