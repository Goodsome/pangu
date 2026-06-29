from code_structure.domain.aggregates.function_symbol import FunctionSymbol
from code_structure.domain.identities.symbol_ids import FunctionId
from code_structure.domain.value_objects.location import Location
from code_structure.infrastructure.orm_models.function_node import FunctionNode
from foundation.common_types.fqns.fqn import FunctionFqn


def str_to_function_id(s: str) -> FunctionId:
    return FunctionId.reconstitute(s)


def function_node_to_function_symbol(function_node: FunctionNode) -> FunctionSymbol:
    return FunctionSymbol(
        id=str_to_function_id(function_node.id),
        name=function_node.name,
        fqn=FunctionFqn(function_node.fqn),
        location=Location(
            start_line=function_node.start_line,
            start_column=function_node.start_column,
            end_line=function_node.end_line,
            end_column=function_node.end_column,
        ),
    )
