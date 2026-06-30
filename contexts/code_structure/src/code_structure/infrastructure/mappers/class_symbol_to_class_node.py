from code_structure.domain.aggregates.class_symbol import ClassSymbol
from code_structure.infrastructure.mappers.attribute_symbol_to_attribute_node import (
    attribute_symbol_to_attribute_node,
)
from code_structure.infrastructure.mappers.method_symbol_to_method_node import (
    method_symbol_to_method_node,
)
from code_structure.infrastructure.orm_models.class_node import ClassNode


def class_symbol_to_class_node(class_symbol: ClassSymbol) -> ClassNode:
    attributes = [
        attribute_symbol_to_attribute_node(attr)
        for attr in class_symbol.attributes.values()
    ]
    methods = [
        method_symbol_to_method_node(method) for method in class_symbol.methods.values()
    ]
    return ClassNode(
        id=str(class_symbol.id),
        name=class_symbol.name,
        fqn=class_symbol.fqn,
        attributes=attributes,
        methods=methods,
    )
