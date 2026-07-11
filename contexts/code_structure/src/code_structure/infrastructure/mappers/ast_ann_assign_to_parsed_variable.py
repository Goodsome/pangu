from code_structure.domain.value_objects.parsed_variable import ParsedVariable
from code_structure.infrastructure.visitors.reference_visitor import VariableVisitor
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_ann_assign import AstAnnAssign
from codegen.code_metadata.domain.value_objects.ast_name import AstName
from foundation.common_types.fqns.fqn import SymbolFqn


def ast_ann_assign_to_parsed_variable(
    node: AstAnnAssign,
    scope_symbols: dict[str, SymbolFqn],
) -> ParsedVariable:
    if not isinstance(node.target, AstName):
        raise ValueError("Target must be a Name node")
    name = node.target.id

    ref_visitor = VariableVisitor(scope_symbols=scope_symbols)
    ref_visitor.visit(node)

    return ParsedVariable(name=name, references=ref_visitor.references)
