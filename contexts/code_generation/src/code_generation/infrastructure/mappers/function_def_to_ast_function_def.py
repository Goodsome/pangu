from code_dom.domain.value_objects.ast_stmt import AstFunctionDef
from code_generation.domain.value_objects.symbol_def import FunctionDef


def function_def_to_ast_function_def(function_def: FunctionDef) -> AstFunctionDef:
    return AstFunctionDef(
        lineno=0,
        name=function_def.name,
    )