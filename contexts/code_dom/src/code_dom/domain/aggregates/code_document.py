from itertools import groupby
from operator import itemgetter
from pathlib import Path
from code_dom.domain.visitors.update_imports_visitor import UpdateImportsVisitor
from codegen.code_metadata.domain.value_objects.ast_alias import AstAlias
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_import_from import AstImportFrom
from codegen.code_metadata.domain.value_objects.ast_stmt import AstStmt
from foundation.building_blocks.aggregate_root import AggregateRoot
from foundation.integration_events.class_moved import ModuleDepDict
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_class_def import (
    AstClassDef,
)


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

    def set_imports(self, deps: list[ModuleDepDict]) -> None:
        """Rebuild all ``from ... import`` statements from a dependency list.

        Non-import statements are preserved. Existing ``from`` imports are
        fully replaced by the new set derived from *deps*.
        """
        non_import_body = [s for s in self.body if not isinstance(s, AstImportFrom)]
        self.body = _build_imports_from_deps(deps) + non_import_body

    def move_class_import(
        self, class_name: str, old_module: str, new_module: str
    ) -> None:
        """Move a single class import from old_module to new_module.

        Handles the case where ``from old_module import MyClass, OtherClass``
        must be split: ``OtherClass`` stays with ``old_module``, ``MyClass``
        moves to ``new_module``.
        """
        target_import = _find_import_from(self.body, new_module)
        alias_to_move: AstAlias | None = None
        new_body: list[AstStmt] = []
        for stmt in self.body:
            if not (isinstance(stmt, AstImportFrom) and stmt.module == old_module):
                new_body.append(stmt)
                continue
            remaining = [a for a in stmt.names if a.name != class_name]
            if alias_to_move is None:
                alias_to_move = next(
                    (a for a in stmt.names if a.name == class_name), None
                )
            if remaining:
                new_body.append(stmt.model_copy(update={"names": remaining}))
        if alias_to_move is None:
            return
        if target_import is not None:
            target_import.names.append(alias_to_move)
        else:
            insert_at = _last_import_index(new_body)
            new_body.insert(
                insert_at, AstImportFrom(module=new_module, names=[alias_to_move])
            )
        self.body = new_body

    def remove_class(self, class_name: str) -> AstClassDef | None:
        for stmt in self.body:
            if isinstance(stmt, AstClassDef) and stmt.name == class_name:
                self.body = [s for s in self.body if s is not stmt]
                return stmt
        return None

    def add_class(self, class_def: AstClassDef) -> None:
        self.body.append(class_def)


def _last_import_index(body: list[AstStmt]) -> int:
    """Return the index after the last import statement, or 0."""
    for i in range(len(body) - 1, -1, -1):
        if isinstance(body[i], AstImportFrom):
            return i + 1
    return 0


def _find_import_from(body: list[AstStmt], module: str) -> AstImportFrom | None:
    for stmt in body:
        if isinstance(stmt, AstImportFrom) and stmt.module == module:
            return stmt
    return None


def _build_imports_from_deps(deps: list[ModuleDepDict]) -> list[AstImportFrom]:
    """Group deps by (module, alias) and build one AstImportFrom per group."""
    if not deps:
        return []
    sorted_deps = sorted(deps, key=itemgetter("module"))
    imports: list[AstImportFrom] = []
    for module, group in groupby(sorted_deps, key=itemgetter("module")):
        names = [AstAlias(name=d["symbol"], asname=d.get("alias")) for d in group]
        imports.append(AstImportFrom(module=module, names=names))
    return imports
