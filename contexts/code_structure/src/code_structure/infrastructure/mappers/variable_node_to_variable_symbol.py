from code_structure.domain.aggregates.variable_symbol import VariableSymbol
from code_structure.domain.identities.symbol_ids import VariableId
from code_structure.domain.value_objects.location import Location
from code_structure.infrastructure.orm_models.variable_node import VariableNode
from foundation.common_types.fqns.fqn import VariableFqn


def str_to_variable_id(s: str) -> VariableId:
    return VariableId.reconstitute(s)


def variable_node_to_variable_symbol(variable_node: VariableNode) -> VariableSymbol:
    return VariableSymbol(
        id=str_to_variable_id(variable_node.id),
        name=variable_node.name,
        fqn=VariableFqn(variable_node.fqn),
        location=Location(
            start_line=variable_node.start_line,
            start_column=variable_node.start_column,
            end_line=variable_node.end_line,
            end_column=variable_node.end_column,
        ),
    )
