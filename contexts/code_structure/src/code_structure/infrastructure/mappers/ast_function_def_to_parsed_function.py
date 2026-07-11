from code_structure.domain.value_objects.parsed_function import ParsedFunction
from code_structure.infrastructure.visitors.reference_visitor import FunctionVisitor
from codegen.code_metadata.domain.value_objects.ast_stmt import AstFunctionDef
from foundation.common_types.fqns.fqn import SymbolFqn


def ast_function_def_to_parsed_function(
    node: AstFunctionDef,
    scope_symbols: dict[str, SymbolFqn],
) -> ParsedFunction:
    ref_visitor = FunctionVisitor(scope_symbols=scope_symbols)
    ref_visitor.visit(node)
    return ParsedFunction(
        name=node.name,
        references=ref_visitor.references,
    )
