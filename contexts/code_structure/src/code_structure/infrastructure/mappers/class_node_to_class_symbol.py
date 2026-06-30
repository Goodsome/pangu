from code_structure.domain.aggregates.class_symbol import ClassSymbol
from code_structure.domain.identities.symbol_ids import ClassId
from code_structure.infrastructure.orm_models.class_node import ClassNode
from foundation.common_types.fqns.fqn import ClassFqn


def str_to_class_id(s: str) -> ClassId:
    return ClassId.reconstitute(s)


def class_node_to_class_symbol(class_node: ClassNode) -> ClassSymbol:
    return ClassSymbol(
        id=str_to_class_id(class_node.id),
        name=class_node.name,
        fqn=ClassFqn(class_node.fqn),
    )
