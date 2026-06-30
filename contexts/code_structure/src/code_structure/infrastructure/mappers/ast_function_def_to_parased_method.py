from code_structure.domain.value_objects.parsed_method import ParsedMethod
from codegen.code_metadata.domain.value_objects.ast_stmt_old import AstFunctionDef


def ast_function_def_to_parsed_method(node: AstFunctionDef) -> ParsedMethod:
    return ParsedMethod(
        name=node.name,
    )
