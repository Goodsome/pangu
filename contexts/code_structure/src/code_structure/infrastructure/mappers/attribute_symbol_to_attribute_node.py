from code_structure.domain.entities.attribute_symbol import AttributeSymbol
from code_structure.infrastructure.orm_models.attribute_node import AttributeNode


def attribute_symbol_to_attribute_node(
    attribute_symbol: AttributeSymbol,
) -> AttributeNode:
    return AttributeNode(
        id=str(attribute_symbol.id),
        name=attribute_symbol.name,
        fqn=attribute_symbol.fqn,
    )
