from code_structure.domain.value_objects.parsed_function import ParsedFunction
from codegen.code_metadata.domain.value_objects.ast_stmt_old import AstFunctionDef


def ast_function_def_to_parsed_function(node: AstFunctionDef) -> ParsedFunction:
    return ParsedFunction(
        name=node.name,
    )
