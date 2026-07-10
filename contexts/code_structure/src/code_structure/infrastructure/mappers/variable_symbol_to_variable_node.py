from code_structure.domain.aggregates.variable_symbol import VariableSymbol
from code_structure.infrastructure.orm_models.variable_node import VariableNode


from foundation.persistence.orm.neo4j_base import OutEdge
from code_structure.infrastructure.orm_models.edges import ReferencesEdge


def variable_symbol_to_variable_node(variable_symbol: VariableSymbol) -> VariableNode:
    references = [
        ReferencesEdge(
            source_ref=str(variable_symbol.fqn),
            target_ref=str(ref.target_fqn),
            alias=ref.alias,
        )
        for ref in variable_symbol.references
    ]
    return VariableNode(
        id=str(variable_symbol.id),
        name=variable_symbol.name,
        fqn=variable_symbol.fqn,
        references=OutEdge(items=references),
    )
