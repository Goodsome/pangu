from code_structure.domain.entities.method_symbol import MethodSymbol
from code_structure.infrastructure.orm_models.method_node import MethodNode


def method_symbol_to_method_node(method_symbol: MethodSymbol) -> MethodNode:
    return MethodNode(
        id=str(method_symbol.id),
        name=method_symbol.name,
        fqn=method_symbol.fqn,
    )
