from abc import ABC
from abc import abstractmethod
from collections.abc import Collection
from codegen.code_metadata.domain.aggregates.component import Component
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.application.dtos.component_filter import ComponentFilter
from codegen.shared.application.dtos.page import Page
from codegen.shared.application.dtos.page_query import PageQuery
from codegen.shared.domain.ports.repository import Repository


class ComponentRepository(Repository[Component, ComponentId], ABC):
    """Component repository interface."""

    @abstractmethod
    def find_page(self, page_query: PageQuery[ComponentFilter]) -> Page[Component]: ...

    @abstractmethod
    def find_by_context_names(
        self, context_names: set[tuple[str, str]]
    ) -> dict[tuple[str, str], Component]: ...

    @abstractmethod
    def find_by_contexts(
        self, contexts: set[str]
    ) -> dict[tuple[str, str], Component]: ...

    @abstractmethod
    def find_by_ids(
        self, ids: Collection[ComponentId]
    ) -> dict[ComponentId, Component]: ...
