import ast
from dataclasses import dataclass
from pathlib import Path
from typing import override
from code_dom.domain.aggregates.code_document import CodeDocument
from code_dom.domain.ports.code_parser import CodeParser
from code_dom.infrastructure.mappers.ast_to_stmt import AstToStmt
from foundation.system.file_system_port import FileSystemPort


@dataclass
class ASTCodeParser(CodeParser):
    file_system: FileSystemPort

    @override
    def parse_file(self, path: Path) -> CodeDocument:
        code = self.file_system.read_file(path)
        ast_module = ast.parse(code)
        body = [AstToStmt.to_stmt(node) for node in ast_module.body]
        description = ast.get_docstring(ast_module)
        if description:
            body = body[1:]
        return CodeDocument(
            id=path, physical_path=path, body=body, description=description
        )

    @override
    def parse_directory(self, path: Path) -> list[CodeDocument]:
        files = self.file_system.list_directory_recursively(path, pattern="*.py")
        return [self.parse_file(file) for file in files]
