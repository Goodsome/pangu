from pathlib import Path
from codegen.code_dom.domain.visitors.update_imports_visitor import UpdateImportsVisitor
from codegen.code_metadata.domain.value_objects.ast_stmt_old import AstStmt
from codegen.shared.domain.core.aggregate_root import AggregateRoot


class CodeDocument(AggregateRoot[Path]):
    physical_path: Path
    body: list[AstStmt]
    description: str | None

    @property
    def is_init_file(self) -> bool:
        return self.physical_path.name == "__init__.py"

    def update_imports(self, old_module: str, new_module: str) -> None:
        update_imports_visitor = UpdateImportsVisitor(old_module, new_module)
        update_imports_visitor.visit(self.body)