from abc import ABC
from abc import abstractmethod
from codegen.code_metadata.application.dtos.module_dto import ModuleDto
from codegen.code_metadata.application.dtos.module_filter import ModuleFilter
from codegen.shared.application.dtos.page import Page
from codegen.shared.application.dtos.page_query import PageQuery


class ModuleQueryService(ABC):

    @abstractmethod
    def find_page(self, page_query: PageQuery[ModuleFilter]) -> Page[ModuleDto]: ...

    @abstractmethod
    def find_by_filter(self, filter: ModuleFilter) -> list[ModuleDto]: ...
