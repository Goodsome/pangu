from code_structure.domain.value_objects.parsed_class import ParsedClass
from code_structure.infrastructure.visitors.class_visitor import ClassVisitor
from foundation.common_types.fqns.fqn import SymbolFqn
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_class_def import (
    AstClassDef,
)


def ast_class_def_to_parsed_class(
    node: AstClassDef, scope_symbols: dict[str, SymbolFqn]
) -> ParsedClass:
    class_visitor = ClassVisitor(scope_symbols=scope_symbols)
    class_visitor.visit(node)
    return ParsedClass(
        name=node.name,
        variables=class_visitor.variables,
        functions=class_visitor.functions,
        references=class_visitor.references,
    )
