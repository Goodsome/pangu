from code_structure.domain.aggregates.class_symbol import ClassSymbol
from code_structure.infrastructure.mappers.attribute_symbol_to_attribute_node import (
    attribute_symbol_to_attribute_node,
)
from code_structure.infrastructure.mappers.method_symbol_to_method_node import (
    method_symbol_to_method_node,
)
from code_structure.infrastructure.orm_models.class_node import ClassNode
from code_structure.infrastructure.orm_models.attribute_node import AttributeNode
from code_structure.infrastructure.orm_models.method_node import MethodNode
from code_structure.infrastructure.orm_models.symbol_node import SymbolNode
from foundation.persistence.orm.neo4j_base import OutNode, OutEdge, EdgeItem
from code_structure.infrastructure.orm_models.edges import (
    ReferencesEdge,
    ClassDefinesEdge,
)


def class_symbol_to_class_node(class_symbol: ClassSymbol) -> ClassNode:
    class_id_str = str(class_symbol.id)

    attributes: list[EdgeItem[ClassDefinesEdge, AttributeNode]] = []
    for attr in class_symbol.attributes.values():
        attr_node = attribute_symbol_to_attribute_node(attr)
        attributes.append(
            EdgeItem(
                edge=ClassDefinesEdge(source_ref=class_id_str, target_ref=attr_node.id),
                target=attr_node,
            )
        )

    methods: list[EdgeItem[ClassDefinesEdge, MethodNode]] = []
    for method in class_symbol.methods.values():
        method_node = method_symbol_to_method_node(method)
        methods.append(
            EdgeItem(
                edge=ClassDefinesEdge(
                    source_ref=class_id_str, target_ref=method_node.id
                ),
                target=method_node,
            )
        )

    references: list[EdgeItem[ReferencesEdge, SymbolNode]] = []
    for ref in class_symbol.references:
        references.append(
            EdgeItem(
                edge=ReferencesEdge(
                    source_ref=class_id_str,
                    target_ref=str(ref.target_fqn),
                    alias=ref.alias,
                )
            )
        )

    return ClassNode(
        id=class_id_str,
        name=class_symbol.name,
        fqn=class_symbol.fqn,
        attributes=OutNode(items=attributes),
        methods=OutNode(items=methods),
        references=OutEdge(items=references),
    )
