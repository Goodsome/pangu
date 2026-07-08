from code_structure.domain.aggregates.external_symbol import ExternalSymbol
from code_structure.domain.identities.symbol_ids import ExternalSymbolId
from code_structure.infrastructure.orm_models.external_symbol_node import (
    ExternalSymbolNode,
)
from foundation.common_types.fqns.fqn import SymbolFqn


def external_symbol_node_to_external_symbol(node: ExternalSymbolNode) -> ExternalSymbol:
    return ExternalSymbol(
        id=ExternalSymbolId.reconstitute(node.id),
        name=node.name,
        fqn=SymbolFqn(node.fqn),
    )


def external_symbol_to_external_symbol_node(
    symbol: ExternalSymbol,
) -> ExternalSymbolNode:
    return ExternalSymbolNode(
        id=str(symbol.id),
        name=symbol.name,
        fqn=symbol.fqn,
    )
