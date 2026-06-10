from abc import ABC
from abc import abstractmethod
from pathlib import Path
from codegen.code_metadata.application.dtos.parsed_component import ParsedComponent
from codegen.code_metadata.application.dtos.parsed_module import ParsedDirectoryModule
from codegen.code_metadata.application.dtos.parsed_module import ParsedFileModule


class CodeParser(ABC):

    @abstractmethod
    def parse(self, code: str, component_name: str) -> ParsedComponent: ...

    @abstractmethod
    def parse_module(self, code: str, path: Path) -> ParsedFileModule: ...

    @abstractmethod
    def parse_init_module(self, code: str, path: Path) -> ParsedDirectoryModule: ...
