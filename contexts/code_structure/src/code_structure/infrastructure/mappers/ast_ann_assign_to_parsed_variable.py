from code_structure.domain.value_objects.parsed_variable import ParsedVariable
from codegen.code_metadata.domain.value_objects.ast_ann_assign import AstAnnAssign
from codegen.code_metadata.domain.value_objects.ast_name import AstName


def ast_ann_assign_to_parsed_variable(
    node: AstAnnAssign,
) -> ParsedVariable:
    if not isinstance(node.target, AstName):
        raise ValueError("Target must be a Name node")
    name = node.target.id
    return ParsedVariable(name=name)
