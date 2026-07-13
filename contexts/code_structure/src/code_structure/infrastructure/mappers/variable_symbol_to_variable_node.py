from code_structure.domain.aggregates.variable_symbol import VariableSymbol
from code_structure.infrastructure.orm_models.variable_node import VariableNode
from code_structure.infrastructure.orm_models.symbol_node import SymbolNode

from foundation.persistence.orm.neo4j_base import OutEdge, EdgeItem
from code_structure.infrastructure.orm_models.edges import ReferencesEdge


def variable_symbol_to_variable_node(
    variable_symbol: VariableSymbol,
) -> VariableNode:
    references: list[EdgeItem[ReferencesEdge, SymbolNode]] = [
        EdgeItem(
            edge=ReferencesEdge(
                source_ref=str(variable_symbol.id),
                target_ref=str(ref.target_fqn),
                alias=ref.alias,
            )
        )
        for ref in variable_symbol.references
    ]
    return VariableNode(
        id=str(variable_symbol.id),
        name=variable_symbol.name,
        fqn=variable_symbol.fqn,
        references=OutEdge(items=references),
    )
