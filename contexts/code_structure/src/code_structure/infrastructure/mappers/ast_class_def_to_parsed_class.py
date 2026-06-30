from code_structure.domain.value_objects.parsed_class import ParsedClass
from codegen.code_metadata.domain.value_objects.ast_stmt_old import AstClassDef


def ast_class_def_to_parsed_class(node: AstClassDef) -> ParsedClass:
    return ParsedClass(
        name=node.name,
    )