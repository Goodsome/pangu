import ast

from code_dom.domain.value_objects.ast_expr import AstExprBase
from code_dom.domain.value_objects.ast_expr.ast_name import AstName
from code_dom.domain.value_objects.ast_expr.ast_subscript import AstSubscript
from code_dom.domain.value_objects.ast_expr.ast_tuple import AstTuple
from code_dom.domain.value_objects.ast_stmt import (
    AstAnnAssign,
    AstAssign,
    AstClassDef,
    AstFunctionDef,
    AstPass,
    AstStmtBase,
)
from code_dom.infrastructure.mappers.ast_to_stmt import AstToStmt
from foundation.common_types.snake_string import SnakeString


def make_generic_base(
    base_name: str, generic_args: list[str] | None = None
) -> AstExprBase:
    if not generic_args:
        return AstName(id=base_name)
    if len(generic_args) == 1:
        slice_expr: AstExprBase = AstName(id=generic_args[0])
    else:
        slice_expr = AstTuple(elts=[AstName(id=arg) for arg in generic_args])
    return AstSubscript(value=AstName(id=base_name), slice=slice_expr)


def make_class(
    name: str,
    bases: list[AstExprBase] | None = None,
    body: list[AstStmtBase] | None = None,
    decorators: list[str] | None = None,
) -> AstClassDef:
    return AstClassDef(
        name=name,
        bases=bases or [],
        keywords=[],
        body=body or [],
        decorator_list=[AstName(id=d) for d in (decorators or [])],
    )


def make_func(
    name: str,
    params: list[tuple[str, str | None]] | None = None,
    returns: str | None = None,
    body: list[AstStmtBase] | None = None,
    decorators: list[str] | None = None,
    is_async: bool = False,
) -> AstFunctionDef:
    arguments: list[AstAssign | AstAnnAssign] = []
    for param_name, annotation in params or []:
        if annotation:
            arguments.append(
                AstAnnAssign(
                    target=AstName(id=param_name),
                    annotation=AstName(id=annotation),
                    value=None,
                )
            )
        else:
            arguments.append(
                AstAssign(
                    targets=[AstName(id=param_name)],
                    value=None,
                )
            )
    return AstFunctionDef(
        lineno=0,
        is_async=is_async,
        name=name,
        arguments=arguments,
        decorator_list=[AstName(id=d) for d in (decorators or [])],
        returns=AstName(id=returns) if returns else None,
        body=body or [AstPass()],
    )


def parse_body(code: str) -> list[AstStmtBase]:
    parsed = ast.parse(code.strip())
    return [AstToStmt.to_stmt(stmt) for stmt in parsed.body]


def to_plural(name: str) -> str:
    s = str(SnakeString(name))
    if s.endswith("y") and not s.endswith(("ay", "ey", "iy", "oy", "uy")):
        return s[:-1] + "ies"
    elif s.endswith(("s", "sh", "ch", "x", "z")):
        return s + "es"
    return s + "s"
