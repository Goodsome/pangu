from code_structure.domain.aggregates.function_symbol import FunctionSymbol
from code_structure.infrastructure.orm_models.function_node import FunctionNode
from code_structure.infrastructure.orm_models.symbol_node import SymbolNode

from foundation.persistence.orm.neo4j_base import OutEdge, EdgeItem
from code_structure.infrastructure.orm_models.edges import ReferencesEdge


def function_symbol_to_function_node(
    function_symbol: FunctionSymbol,
) -> FunctionNode:
    references: list[EdgeItem[ReferencesEdge, SymbolNode]] = [
        EdgeItem(
            edge=ReferencesEdge(
                source_ref=str(function_symbol.id),
                target_ref=str(ref.target_fqn),
                alias=ref.alias,
            )
        )
        for ref in function_symbol.references
    ]
    return FunctionNode(
        id=str(function_symbol.id),
        name=function_symbol.name,
        fqn=function_symbol.fqn,
        references=OutEdge(items=references),
    )
