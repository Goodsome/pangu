import ast
from typing import override
from code_dom.domain.services.ast_visitor import AstVisitor
from code_dom.domain.value_objects.ast_stmt.ast_for import AstFor
from code_dom.infrastructure.mappers.ast_to_stmt import AstToStmt
from code_dom.infrastructure.mappers.stmt_to_ast import StmtToAst


def test_ast_to_stmt_async_for() -> None:
    code = "async for item in iterable:\n    print(item)\nelse:\n    pass"
    module = ast.parse(code)
    async_for_ast = module.body[0]
    assert isinstance(async_for_ast, ast.AsyncFor)

    stmt = AstToStmt.to_stmt(async_for_ast)
    assert isinstance(stmt, AstFor)
    assert stmt.is_async is True

    # Test reverse conversion
    converted_ast = StmtToAst.to_node(stmt)
    assert isinstance(converted_ast, ast.AsyncFor)
    assert ast.unparse(converted_ast) == ast.unparse(async_for_ast)


def test_ast_visitor_async_for() -> None:
    code = "async for item in iterable:\n    pass"
    module = ast.parse(code)
    async_for_ast = module.body[0]
    stmt = AstToStmt.to_stmt(async_for_ast)

    visited_nodes: list[AstFor] = []

    class DummyVisitor(AstVisitor):
        @override
        def visit_ast_for(self, node: AstFor) -> None:
            visited_nodes.append(node)
            super().visit_ast_for(node)

    visitor = DummyVisitor()
    visitor.visit(stmt)

    assert len(visited_nodes) == 1
    assert visited_nodes[0] is stmt
