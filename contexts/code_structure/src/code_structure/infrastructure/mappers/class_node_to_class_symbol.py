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


def str_to_class_id(s: str) -> ClassId:
    return ClassId.reconstitute(s)


def class_node_to_class_symbol(class_node: ClassNode) -> ClassSymbol:
    attributes = {
        AttributeId.reconstitute(a.id): attribute_node_to_attribute_symbol(a)
        for a in class_node.attributes
    }
    methods = {
        MethodId.reconstitute(m.id): method_node_to_method_symbol(m)
        for m in class_node.methods
    }
    return ClassSymbol(
        id=str_to_class_id(class_node.id),
        name=class_node.name,
        fqn=ClassFqn(class_node.fqn),
        attributes=attributes,
        methods=methods,
    )
