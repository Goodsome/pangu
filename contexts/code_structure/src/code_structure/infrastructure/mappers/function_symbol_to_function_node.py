from code_structure.domain.aggregates.function_symbol import FunctionSymbol
from code_structure.infrastructure.orm_models.function_node import FunctionNode


from foundation.persistence.orm.neo4j_base import OutEdge
from code_structure.infrastructure.orm_models.edges import ReferencesEdge


def function_symbol_to_function_node(function_symbol: FunctionSymbol) -> FunctionNode:
    references = [
        ReferencesEdge(
            source_ref=str(function_symbol.fqn),
            target_ref=str(ref.target_fqn),
            alias=ref.alias,
        )
        for ref in function_symbol.references
    ]
    return FunctionNode(
        id=str(function_symbol.id),
        name=function_symbol.name,
        fqn=function_symbol.fqn,
        references=OutEdge(items=references),
    )
