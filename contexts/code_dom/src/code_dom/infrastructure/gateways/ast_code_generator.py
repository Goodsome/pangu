import ast
from typing import override
from code_dom.domain.aggregates.code_document import CodeDocument
from code_dom.domain.ports.code_generator import CodeGenerator
from codegen.code_metadata.infrastructure.mappers.stmt_to_ast import StmtToAst


class AstCodeGenerator(CodeGenerator):
    @override
    def generate(self, code_document: CodeDocument) -> str:
        body: list[ast.stmt] = []
        if code_document.description:
            body.append(ast.Expr(value=ast.Constant(value=code_document.description)))
        body.extend([StmtToAst.to_node(b) for b in code_document.body])
        module = ast.Module(body=body)
        ast.fix_missing_locations(module)
        return ast.unparse(module)
