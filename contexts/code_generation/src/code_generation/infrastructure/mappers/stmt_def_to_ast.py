import ast

from code_dom.domain.value_objects.ast_stmt import AstPass, AstStmtBase
from code_dom.infrastructure.mappers.ast_to_stmt import AstToStmt
from code_generation.domain.value_objects.symbol_def import PassDef, RawStmtDef, StmtDef


def stmt_def_to_ast(stmt_def: StmtDef) -> AstStmtBase:
    match stmt_def:
        case PassDef():
            return AstPass()
        case RawStmtDef(code=code):
            parsed_ast = ast.parse(code).body[0]
            return AstToStmt.to_stmt(parsed_ast)
