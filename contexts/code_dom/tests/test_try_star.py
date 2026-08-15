import ast
from typing import override

from code_dom.domain.services.ast_visitor import AstVisitor
from code_dom.domain.value_objects.ast_stmt.ast_try import AstTry
from code_dom.infrastructure.mappers.ast_to_stmt import AstToStmt
from code_dom.infrastructure.mappers.stmt_to_ast import StmtToAst


def test_try_star_ast_to_stmt():
    code = """
try:
    do_something()
except* ValueError as e:
    handle_val(e)
except* (TypeError, KeyError):
    handle_other()
else:
    no_error()
finally:
    cleanup()
"""
    parsed_ast = ast.parse(code)
    try_star_ast = parsed_ast.body[0]
    assert isinstance(try_star_ast, ast.TryStar)

    stmt = AstToStmt.to_stmt(try_star_ast)
    assert isinstance(stmt, AstTry)
    assert stmt.is_star is True
    assert len(stmt.handlers) == 2
    assert stmt.handlers[0].name == "e"
    assert len(stmt.orelse) == 1
    assert len(stmt.finalbody) == 1


def test_try_star_stmt_to_ast():
    code = """
try:
    do_something()
except* ValueError as e:
    handle_val(e)
""".strip()
    parsed_ast = ast.parse(code)
    try_star_ast = parsed_ast.body[0]
    stmt = AstToStmt.to_stmt(try_star_ast)

    converted_ast = StmtToAst.to_node(stmt)
    assert isinstance(converted_ast, ast.TryStar)

    unparsed = ast.unparse(converted_ast)
    assert "except* ValueError as e:" in unparsed


def test_try_star_visitor():
    code = """
try:
    x = 1
except* Exception:
    y = 2
"""
    parsed_ast = ast.parse(code)
    stmt = AstToStmt.to_stmt(parsed_ast.body[0])

    visited_types: list[str] = []

    class DummyVisitor(AstVisitor):
        @override
        def visit(self, node: object) -> None:
            if node is not None:
                visited_types.append(type(node).__name__)
                super().visit(node)  # pyright: ignore[reportArgumentType]

    visitor = DummyVisitor()
    visitor.visit(stmt)

    assert "AstTry" in visited_types
    assert "AstExceptHandler" in visited_types
