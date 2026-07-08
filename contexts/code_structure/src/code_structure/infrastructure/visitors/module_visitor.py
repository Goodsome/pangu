from dataclasses import dataclass, field
from typing_extensions import override

from code_dom.domain.services.ast_visitor import AstVisitor
from code_structure.domain.value_objects.parsed_class import ParsedClass
from code_structure.domain.value_objects.parsed_function import ParsedFunction
from code_structure.domain.value_objects.parsed_import import ParsedImport
from code_structure.domain.value_objects.parsed_variable import ParsedVariable
from code_structure.infrastructure.mappers.ast_ann_assign_to_parsed_variable import (
    ast_ann_assign_to_parsed_variable,
)
from code_structure.infrastructure.mappers.ast_assgin_to_parsed_variable import (
    ast_assign_to_parsed_variable,
)
from code_structure.infrastructure.mappers.ast_class_def_to_parsed_class import (
    ast_class_def_to_parsed_class,
)
from code_structure.infrastructure.mappers.ast_function_def_to_parsed_function import (
    ast_function_def_to_parsed_function,
)
from codegen.code_metadata.domain.value_objects.ast_ann_assign import AstAnnAssign
from codegen.code_metadata.domain.value_objects.ast_assign import AstAssign
from codegen.code_metadata.domain.value_objects.ast_import import AstImport
from codegen.code_metadata.domain.value_objects.ast_import_from import AstImportFrom
from codegen.code_metadata.domain.value_objects.ast_stmt_old import (
    AstClassDef,
    AstFunctionDef,
)
from foundation.common_types.fqns.fqn import ModuleFqn, SymbolFqn


@dataclass
class ModuleVistior(AstVisitor):
    module_fqn: ModuleFqn

    classes: list[ParsedClass] = field(default_factory=list)
    functions: list[ParsedFunction] = field(default_factory=list)
    variables: list[ParsedVariable] = field(default_factory=list)
    imports: list[ParsedImport] = field(default_factory=list)

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

    @override
    def visit_ast_import(self, node: AstImport):
        pass

    @override
    def visit_ast_import_from(self, node: AstImportFrom):
        if node.level > 0:
            current_prefix = self.module_fqn
            for _ in range(node.level):
                if current_prefix:
                    current_prefix = current_prefix.parent_fqn
            module_prefix = current_prefix
        else:
            module_prefix = ""

        module = node.module or ""
        if module_prefix:
            if module:
                module = f"{module_prefix}.{module}"
            else:
                module = str(module_prefix)

        if not module:
            return

        for name in node.names:
            target_fqn = SymbolFqn(f"{module}::{name.name}")
            self.imports.append(ParsedImport(target_fqn=target_fqn, alias=name.asname))
