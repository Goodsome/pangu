import ast
from dataclasses import dataclass
from pathlib import Path
from typing import override
from codegen.code_metadata.application.dtos.parsed_component import ParsedComponent
from codegen.code_metadata.application.dtos.parsed_module import ParsedDirectoryModule
from codegen.code_metadata.application.dtos.parsed_module import ParsedFileModule
from codegen.code_metadata.application.ports.code_parser import CodeParser
from codegen.code_metadata.infrastructure.mappers.ast_module_to_component import (
    AstModuleToComponent,
)


@dataclass
class PythonCodeParser(CodeParser):

    @override
    def parse(self, code: str, component_name: str) -> ParsedComponent:
        mapper = AstModuleToComponent()
        module = ast.parse(code)
        return mapper.map(module, component_name=component_name)

    @override
    def parse_module(self, code: str, path: Path) -> ParsedFileModule:
        mapper = AstModuleToComponent()
        module = ast.parse(code)
        parsed_file_module = mapper.parse_module(module=module, path=path)
        return parsed_file_module

    @override
    def parse_init_module(self, code: str, path: Path) -> ParsedDirectoryModule:
        mapper = AstModuleToComponent()
        module = ast.parse(code)
        parsed_directory_module = mapper.parse_init_module(module=module, path=path)
        return parsed_directory_module
