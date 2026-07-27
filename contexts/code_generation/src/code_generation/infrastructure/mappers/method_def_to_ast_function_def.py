from code_dom.domain.value_objects.ast_expr import AstExprBase
from code_dom.domain.value_objects.ast_expr.ast_name import AstName
from code_dom.domain.value_objects.ast_stmt import AstAssign, AstFunctionDef, AstPass
from code_generation.domain.value_objects.symbol_def import MethodDef


def method_def_to_ast_function_def(method_def: MethodDef) -> AstFunctionDef:
    decorator_list: list[AstExprBase] = [AstName(id=dec) for dec in method_def.decorators]
    returns = AstName(id=method_def.return_type) if method_def.return_type else None

    arguments = [
        AstAssign(targets=[AstName(id=param)], value=None)
        for param in method_def.params
    ]

    return AstFunctionDef(
        lineno=0,
        name=method_def.name,
        arguments=arguments,
        decorator_list=decorator_list,
        returns=returns,
        body=[AstPass()],
    )
