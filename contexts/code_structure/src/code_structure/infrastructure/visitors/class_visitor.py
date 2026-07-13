from dataclasses import dataclass, field
from typing import override

from code_structure.domain.value_objects.parsed_function import ParsedFunction
from code_structure.domain.value_objects.parsed_variable import ParsedVariable
from code_structure.infrastructure.visitors.reference_visitor import ReferenceVisitor
from code_structure.infrastructure.mappers.ast_ann_assign_to_parsed_variable import (
    ast_ann_assign_to_parsed_variable,
)
from code_structure.infrastructure.mappers.ast_assgin_to_parsed_variable import (
    ast_assign_to_parsed_variable,
)
from code_structure.infrastructure.mappers.ast_function_def_to_parsed_function import (
    ast_function_def_to_parsed_function,
)
from code_dom.domain.value_objects.ast_stmt.ast_ann_assign import AstAnnAssign
from code_dom.domain.value_objects.ast_stmt.ast_assign import AstAssign
from code_dom.domain.value_objects.ast_stmt import AstFunctionDef


@dataclass
class ClassVisitor(ReferenceVisitor):
    variables: list[ParsedVariable] = field(default_factory=list, init=False)
    functions: list[ParsedFunction] = field(default_factory=list, init=False)

    @override
    def visit_ast_function_def(self, node: AstFunctionDef):
        parsed_function = ast_function_def_to_parsed_function(
            node,
            scope_symbols=self.scope_symbols,
        )
        self.functions.append(parsed_function)

    @override
    def visit_ast_assign(self, node: AstAssign):
        parsed_variable = ast_assign_to_parsed_variable(
            node,
            scope_symbols=self.scope_symbols,
        )
        self.variables.append(parsed_variable)

    @override
    def visit_ast_ann_assign(self, node: AstAnnAssign):
        parsed_variable = ast_ann_assign_to_parsed_variable(
            node,
            scope_symbols=self.scope_symbols,
        )
        self.variables.append(parsed_variable)
