from code_structure.domain.value_objects.parsed_class import ParsedClass
from code_structure.infrastructure.visitors.class_visitor import ClassVisitor
from codegen.code_metadata.domain.value_objects.ast_stmt_old import AstClassDef


def ast_class_def_to_parsed_class(node: AstClassDef) -> ParsedClass:
    class_visitor = ClassVisitor()
    class_visitor.visit(node)
    return ParsedClass(
        name=node.name,
        attributes=class_visitor.attributes,
        methods=class_visitor.methods,
    )
