import ast
from code_dom.domain.value_objects.ast_stmt.ast_global_nonlocal import (
    AstGlobal,
    AstNonlocal,
)
from code_dom.infrastructure.mappers.ast_to_stmt import AstToStmt
from code_dom.infrastructure.mappers.stmt_to_ast import StmtToAst


def test_global_conversion():
    code = "global x, y"
    ast_node = ast.parse(code).body[0]
    assert isinstance(ast_node, ast.Global)

    stmt = AstToStmt.to_stmt(ast_node)
    assert isinstance(stmt, AstGlobal)
    assert stmt.names == ["x", "y"]

    converted_ast = StmtToAst.to_node(stmt)
    assert isinstance(converted_ast, ast.Global)
    assert converted_ast.names == ["x", "y"]


def test_nonlocal_conversion():
    code = "nonlocal a, b"
    ast_node = ast.parse(code).body[0]
    assert isinstance(ast_node, ast.Nonlocal)

    stmt = AstToStmt.to_stmt(ast_node)
    assert isinstance(stmt, AstNonlocal)
    assert stmt.names == ["a", "b"]

    converted_ast = StmtToAst.to_node(stmt)
    assert isinstance(converted_ast, ast.Nonlocal)
    assert converted_ast.names == ["a", "b"]


def test_visitor_global_nonlocal():
    from code_dom.domain.services.ast_visitor import AstVisitor

    visited = []

    class DummyVisitor(AstVisitor):
        def visit_ast_global(self, node: AstGlobal):
            visited.append("global")

        def visit_ast_nonlocal(self, node: AstNonlocal):
            visited.append("nonlocal")

    visitor = DummyVisitor()
    visitor.visit(AstGlobal(names=["x"]))
    visitor.visit(AstNonlocal(names=["y"]))

    assert visited == ["global", "nonlocal"]

