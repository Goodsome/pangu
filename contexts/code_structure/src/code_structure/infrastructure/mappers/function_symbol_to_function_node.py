from code_structure.domain.aggregates.function_symbol import FunctionSymbol
from code_structure.infrastructure.orm_models.function_node import FunctionNode


def function_symbol_to_function_node(function_symbol: FunctionSymbol) -> FunctionNode:
    return FunctionNode(
        id=str(function_symbol.id),
        name=function_symbol.name,
        fqn=function_symbol.fqn,
        start_line=function_symbol.location.start_line,
        start_column=function_symbol.location.start_column,
        end_line=function_symbol.location.end_line,
        end_column=function_symbol.location.end_column,
    )
