from code_structure.domain.aggregates.class_symbol import ClassSymbol
from code_structure.infrastructure.mappers.attribute_symbol_to_attribute_node import (
    attribute_symbol_to_attribute_node,
)
from code_structure.infrastructure.mappers.method_symbol_to_method_node import (
    method_symbol_to_method_node,
)
from code_structure.infrastructure.orm_models.class_node import ClassNode


from foundation.persistence.orm.neo4j_base import OutNode, OutEdge
from code_structure.infrastructure.orm_models.edges import ReferencesEdge


def class_symbol_to_class_node(class_symbol: ClassSymbol) -> ClassNode:
    attributes = [
        attribute_symbol_to_attribute_node(attr)
        for attr in class_symbol.attributes.values()
    ]
    methods = [
        method_symbol_to_method_node(method) for method in class_symbol.methods.values()
    ]
    references = [
        ReferencesEdge(
            source_ref=str(class_symbol.fqn),
            target_ref=str(ref.target_fqn),
            alias=ref.alias,
        )
        for ref in class_symbol.references
    ]
    return ClassNode(
        id=str(class_symbol.id),
        name=class_symbol.name,
        fqn=class_symbol.fqn,
        attributes=OutNode(items=attributes),
        methods=OutNode(items=methods),
        references=OutEdge(items=references),
    )
