from typing import cast
from code_structure.infrastructure.mappers.method_node_to_method_symbol import (
    method_node_to_method_symbol,
)
from foundation.common_types.fqns.fqn import ClassFqn

from code_structure.domain.aggregates.class_symbol import ClassSymbol
from code_structure.domain.identities.symbol_ids import AttributeId, ClassId, MethodId
from code_structure.infrastructure.mappers.attribute_node_to_attribute_symbol import (
    attribute_node_to_attribute_symbol,
)
from code_structure.infrastructure.orm_models.class_node import ClassNode
from code_structure.infrastructure.orm_models.attribute_node import AttributeNode
from code_structure.infrastructure.orm_models.method_node import MethodNode


def str_to_class_id(s: str) -> ClassId:
    return ClassId.reconstitute(s)


def class_node_to_class_symbol(class_node: ClassNode) -> ClassSymbol:
    attributes = {
        AttributeId.reconstitute(a_id): attribute_node_to_attribute_symbol(
            cast(AttributeNode, a)
        )
        for a_id, a in class_node.attributes.get_nodes_map().items()
    }
    methods = {
        MethodId.reconstitute(m_id): method_node_to_method_symbol(cast(MethodNode, m))
        for m_id, m in class_node.methods.get_nodes_map().items()
    }
    return ClassSymbol(
        id=str_to_class_id(class_node.id),
        name=class_node.name,
        fqn=ClassFqn(class_node.fqn),
        attributes=attributes,
        methods=methods,
    )
