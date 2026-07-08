from code_structure.domain.value_objects.parsed_variable import ParsedVariable
from codegen.code_metadata.domain.value_objects.ast_assign import AstAssign
from codegen.code_metadata.domain.value_objects.ast_name import AstName


def ast_assign_to_parsed_variable(
    node: AstAssign,
) -> ParsedVariable:
    if not isinstance(node.target, AstName):
        raise ValueError("Target must be a Name node")
    name = node.target.id

    return ParsedVariable(name=name)
