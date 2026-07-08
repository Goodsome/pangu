from code_structure.domain.entities.method_symbol import MethodSymbol
from code_structure.domain.identities.symbol_ids import MethodId
from foundation.common_types.fqns.fqn import MethodFqn

from code_structure.infrastructure.orm_models.method_node import MethodNode


def method_node_to_method_symbol(method_node: MethodNode) -> MethodSymbol:
    return MethodSymbol(
        id=MethodId.reconstitute(method_node.id),
        name=method_node.name,
        fqn=MethodFqn(method_node.fqn),
    )
