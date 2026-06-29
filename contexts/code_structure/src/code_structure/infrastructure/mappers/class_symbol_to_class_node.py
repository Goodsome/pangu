from code_structure.domain.aggregates.class_symbol import ClassSymbol
from code_structure.infrastructure.orm_models.class_node import ClassNode


def class_symbol_to_class_node(class_symbol: ClassSymbol) -> ClassNode:
    return ClassNode(
        id=str(class_symbol.id),
        name=class_symbol.name,
        fqn=class_symbol.fqn,
        start_line=class_symbol.location.start_line,
        start_column=class_symbol.location.start_column,
        end_line=class_symbol.location.end_line,
        end_column=class_symbol.location.end_column,
    )
