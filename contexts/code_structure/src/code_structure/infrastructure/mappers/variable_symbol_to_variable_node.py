from code_structure.domain.aggregates.variable_symbol import VariableSymbol
from code_structure.infrastructure.orm_models.variable_node import VariableNode


def variable_symbol_to_variable_node(variable_symbol: VariableSymbol) -> VariableNode:
    return VariableNode(
        id=str(variable_symbol.id),
        name=variable_symbol.name,
        fqn=variable_symbol.fqn,
        start_line=variable_symbol.location.start_line,
        start_column=variable_symbol.location.start_column,
        end_line=variable_symbol.location.end_line,
        end_column=variable_symbol.location.end_column,
    )
