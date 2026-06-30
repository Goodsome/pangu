from dataclasses import dataclass, field
from typing import override

from architecture.domain.services.fqn_service import FqnService
from code_dom.application.queries.get_file_document import (
    GetFileDocumentHandler,
    GetFileDocumentQuery,
)
from code_dom.domain.services.ast_visitor import AstVisitor
from code_structure.domain.value_objects.parsed_class import ParsedClass
from code_structure.domain.value_objects.parsed_function import ParsedFunction
from code_structure.domain.value_objects.parsed_variable import ParsedVariable
from code_structure.infrastructure.mappers.ast_ann_assign_to_parsed_variable import ast_ann_assign_to_parsed_variable
from code_structure.infrastructure.mappers.ast_assgin_to_parsed_variable import ast_assign_to_parsed_variable
from code_structure.infrastructure.mappers.ast_class_def_to_parsed_class import ast_class_def_to_parsed_class
from code_structure.infrastructure.mappers.ast_function_def_to_parsed_function import ast_function_def_to_parsed_function
from codegen.code_metadata.domain.value_objects.ast_stmt_old import AstClassDef, AstFunctionDef
from codegen.code_metadata.domain.value_objects.ast_assign import AstAssign
from codegen.code_metadata.domain.value_objects.ast_ann_assign import AstAnnAssign
from foundation.common_types.fqns.fqn import ModuleFqn

from code_structure.domain.ports.symbol_scanner import SymbolScanner
from code_structure.domain.value_objects.parsed_file_module import ParsedFileModule


@dataclass
class CodeDomScanner(SymbolScanner):
    get_file_document_handler: GetFileDocumentHandler

    @override
    def scan(self, module_fqns: list[ModuleFqn]) -> list[ParsedFileModule]:
        return [self._scan_file_module(module_fqn) for module_fqn in module_fqns]

    def _scan_file_module(self, module_fqn: ModuleFqn) -> ParsedFileModule:
        file_path = FqnService.build_path(module_fqn, is_package=False)
        result = self.get_file_document_handler.execute(
            GetFileDocumentQuery(file_path=file_path)
        )
        code_document = result.code_document
        visitor = SymbolVistior()
        visitor.visit(code_document.body)
        return ParsedFileModule(
            fqn=module_fqn,
            classes=visitor.classes,
            functions=visitor.functions,
            variables=visitor.variables,
        )


@dataclass
class SymbolVistior(AstVisitor):

    classes: list[ParsedClass] = field(default_factory=list)
    functions: list[ParsedFunction] = field(default_factory=list)
    variables: list[ParsedVariable] = field(default_factory=list)

    @override
    def visit_ast_class_def(self, node: AstClassDef):
        parsed_class = ast_class_def_to_parsed_class(node)
        self.classes.append(parsed_class)

    @override
    def visit_ast_function_def(self, node: AstFunctionDef):
        parsed_function = ast_function_def_to_parsed_function(node)
        self.functions.append(parsed_function)

    @override
    def visit_ast_assign(self, node: AstAssign):
        parsed_variable = ast_assign_to_parsed_variable(node)
        self.variables.append(parsed_variable)

    @override
    def visit_ast_ann_assign(self, node: AstAnnAssign):
        parsed_variable = ast_ann_assign_to_parsed_variable(node)
        self.variables.append(parsed_variable)
        
