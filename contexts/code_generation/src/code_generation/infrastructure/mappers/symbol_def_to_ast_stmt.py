from typing import assert_never
from code_dom.domain.value_objects.ast_stmt import AstStmtBase
from code_generation.domain.value_objects.symbol_def import ClassDef, FunctionDef, SymbolDef, VariableDef
from code_generation.infrastructure.mappers.class_def_to_ast_class_def import class_def_to_ast_class_def
from code_generation.infrastructure.mappers.function_def_to_ast_function_def import function_def_to_ast_function_def


def symbol_def_to_ast_stmt(symbol_def: SymbolDef) -> AstStmtBase:
    match symbol_def:
        case ClassDef():
            return class_def_to_ast_class_def(symbol_def)
        case FunctionDef():
            return function_def_to_ast_function_def(symbol_def)
        case VariableDef():
            raise NotImplementedError
        case _:
            assert_never(symbol_def)