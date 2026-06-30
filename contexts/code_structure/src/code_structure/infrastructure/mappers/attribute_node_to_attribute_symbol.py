from foundation.common_types.fqns.fqn import AttributeFqn

from code_structure.domain.entities.attribute_symbol import AttributeSymbol
from code_structure.domain.identities.symbol_ids import AttributeId
from code_structure.infrastructure.orm_models.attribute_node import AttributeNode


def attribute_node_to_attribute_symbol(
    attribute_node: AttributeNode,
) -> AttributeSymbol:
    return AttributeSymbol(
        id=AttributeId.reconstitute(attribute_node.id),
        name=attribute_node.name,
        fqn=AttributeFqn(attribute_node.fqn),
    )
