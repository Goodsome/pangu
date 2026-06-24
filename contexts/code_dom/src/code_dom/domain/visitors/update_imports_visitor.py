from dataclasses import dataclass
from typing import override
from code_dom.domain.services.ast_visitor import AstVisitor
from codegen.code_metadata.domain.value_objects.ast_import import AstImport
from codegen.code_metadata.domain.value_objects.ast_import_from import AstImportFrom


@dataclass
class UpdateImportsVisitor(AstVisitor):
    old_module: str
    new_module: str

    def replace_name(self, name: str) -> str:
        if name == self.old_module:
            return self.new_module
        elif name.startswith(f"{self.old_module}."):
            return f"{self.new_module}.{name[len(self.old_module) + 1 :]}"
        return name

    @override
    def visit_ast_import(self, node: AstImport):
        for name in node.names:
            name.name = self.replace_name(name.name)

    @override
    def visit_ast_import_from(self, node: AstImportFrom):
        if node.module is None:
            return
        node.module = self.replace_name(node.module)
