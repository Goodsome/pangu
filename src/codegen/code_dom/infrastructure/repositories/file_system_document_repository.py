import logging
import ast
from dataclasses import dataclass
from pathlib import Path
from typing import override
from codegen.code_dom.domain.aggregates.code_document import CodeDocument
from codegen.code_dom.domain.ports.code_formatter import CodeFormatter
from codegen.code_dom.domain.repositories.document_repository import DocumentRepository
from codegen.code_metadata.infrastructure.mappers.ast_to_stmt import AstToStmt
from codegen.code_metadata.infrastructure.mappers.stmt_to_ast import StmtToAst
from foundation.system.file_system_port import FileSystemPort

logger = logging.getLogger(__name__)


@dataclass
class FileSystemDocumentRepository(DocumentRepository):
    file_system: FileSystemPort
    code_formatter: CodeFormatter

    @override
    def _add(self, aggregate: CodeDocument) -> None:
        raise NotImplementedError()

    @override
    def _add_all(self, aggregates: list[CodeDocument]) -> None:
        raise NotImplementedError()

    @override
    def _get(self, id: Path) -> CodeDocument:
        code = self.file_system.read_file(id)
        ast_module = ast.parse(code)
        body = [AstToStmt.to_stmt(node) for node in ast_module.body]
        description = ast.get_docstring(ast_module)
        if description:
            body = body[1:]
        return CodeDocument(id=id, physical_path=id, body=body, description=description)

    @override
    def _save(self, aggregate: CodeDocument) -> None:
        body: list[ast.stmt] = []
        if aggregate.description:
            body.append(ast.Expr(value=ast.Constant(value=aggregate.description)))
        body.extend([StmtToAst.to_node(b) for b in aggregate.body])
        module = ast.Module(body=body)
        ast.fix_missing_locations(module)
        code = ast.unparse(module)
        self.file_system.write_file(aggregate.physical_path, code, overwrite=True)
        self.code_formatter.format_path(aggregate.physical_path)

    @override
    def _delete(self, aggregate: CodeDocument) -> None:
        raise NotImplementedError()

    @override
    def _save_all(self, aggregates: list[CodeDocument]) -> None:
        raise NotImplementedError()
