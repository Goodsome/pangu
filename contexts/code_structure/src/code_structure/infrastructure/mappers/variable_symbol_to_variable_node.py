from code_structure.domain.aggregates.variable_symbol import VariableSymbol
from code_structure.infrastructure.orm_models.variable_node import VariableNode


def variable_symbol_to_variable_node(variable_symbol: VariableSymbol) -> VariableNode:
    return VariableNode(
        id=str(variable_symbol.id),
        name=variable_symbol.name,
        fqn=variable_symbol.fqn,
    )
