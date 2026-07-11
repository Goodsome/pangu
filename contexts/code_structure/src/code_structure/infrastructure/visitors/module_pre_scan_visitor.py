from dataclasses import dataclass, field
from typing import override
from code_dom.domain.services.ast_visitor import AstVisitor
from code_structure.domain.value_objects.parsed_import import ParsedImport
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_import_from import AstImportFrom
from codegen.code_metadata.domain.value_objects.ast_stmt import AstFunctionDef
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_assign import AstAssign
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_ann_assign import AstAnnAssign
from codegen.code_metadata.domain.value_objects.ast_name import AstName
from foundation.common_types.fqns.fqn import ModuleFqn, SymbolFqn
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_class_def import (
    AstClassDef,
)


@dataclass
class ModulePreScanVisitor(AstVisitor):
    module_fqn: ModuleFqn
    imports: list[ParsedImport] = field(default_factory=list, init=False)
    local_symbol_names: set[str] = field(default_factory=set, init=False)

    def __post_init__(self):
        super().__init__()
        self.imports = []
        self.local_symbol_names = set()

    @override
    def visit_ast_class_def(self, node: AstClassDef):
        self.local_symbol_names.add(node.name)
        pass

    @override
    def visit_ast_function_def(self, node: AstFunctionDef):
        self.local_symbol_names.add(node.name)
        pass

    @override
    def visit_ast_assign(self, node: AstAssign):
        if isinstance(node.target, AstName):
            self.local_symbol_names.add(node.target.id)
        pass

    @override
    def visit_ast_ann_assign(self, node: AstAnnAssign):
        if isinstance(node.target, AstName):
            self.local_symbol_names.add(node.target.id)
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
