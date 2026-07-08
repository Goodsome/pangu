from dataclasses import dataclass, field
from typing import override

from code_dom.domain.services.ast_visitor import AstVisitor
from code_structure.domain.value_objects.parsed_attribute import ParsedAttribute
from code_structure.domain.value_objects.parsed_method import ParsedMethod
from code_structure.infrastructure.mappers.ast_ann_assign_to_parsed_attribute import (
    ast_ann_assign_to_parsed_attribute,
)
from code_structure.infrastructure.mappers.ast_assgin_to_parsed_attribute import (
    ast_assign_to_parsed_attribute,
)
from code_structure.infrastructure.mappers.ast_function_def_to_parased_method import (
    ast_function_def_to_parsed_method,
)
from codegen.code_metadata.domain.value_objects.ast_ann_assign import AstAnnAssign
from codegen.code_metadata.domain.value_objects.ast_assign import AstAssign
from codegen.code_metadata.domain.value_objects.ast_stmt_old import AstFunctionDef


@dataclass
class ClassVisitor(AstVisitor):
    attributes: list[ParsedAttribute] = field(default_factory=list)
    methods: list[ParsedMethod] = field(default_factory=list)

    @override
    def visit_ast_function_def(self, node: AstFunctionDef):
        parsed_method = ast_function_def_to_parsed_method(node)
        self.methods.append(parsed_method)

    @override
    def visit_ast_assign(self, node: AstAssign):
        parsed_attribute = ast_assign_to_parsed_attribute(node)
        self.attributes.append(parsed_attribute)

    @override
    def visit_ast_ann_assign(self, node: AstAnnAssign):
        parsed_attribute = ast_ann_assign_to_parsed_attribute(node)
        self.attributes.append(parsed_attribute)
