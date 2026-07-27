from code_dom.domain.value_objects.ast_expr import AstExprBase
from code_dom.domain.value_objects.ast_expr.ast_name import AstName
from code_dom.domain.value_objects.ast_stmt import AstFunctionDef
from code_generation.domain.value_objects.symbol_def import FunctionDef
from code_generation.infrastructure.mappers.param_to_ast_assign import param_to_ast_assign
from code_generation.infrastructure.mappers.stmt_def_to_ast import stmt_def_to_ast


def function_def_to_ast_function_def(function_def: FunctionDef) -> AstFunctionDef:
    decorator_list: list[AstExprBase] = [AstName(id=dec) for dec in function_def.decorators]
    returns = AstName(id=function_def.return_type) if function_def.return_type else None
    arguments = [param_to_ast_assign(param) for param in function_def.params]
    body_ast = [stmt_def_to_ast(stmt) for stmt in function_def.body]

    return AstFunctionDef(
        lineno=0,
        name=function_def.name,
        arguments=arguments,
        decorator_list=decorator_list,
        returns=returns,
        body=body_ast,
    )