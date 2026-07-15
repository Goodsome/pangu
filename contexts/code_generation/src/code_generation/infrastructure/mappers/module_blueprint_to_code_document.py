from collections.abc import Mapping

from architecture.domain.services.fqn_service import FqnService
from code_dom.domain.aggregates.code_document import CodeDocument

from code_generation.domain.entities.module_blueprint import ModuleBlueprint
from code_generation.infrastructure.mappers.import_def_to_ast_import_from import (
    import_def_to_ast_import_from,
)
from code_generation.infrastructure.mappers.symbol_def_to_ast_stmt import (
    symbol_def_to_ast_stmt,
)


def module_blueprint_to_code_document(
    module_blueprint: ModuleBlueprint,
    name_module_map: Mapping[str, str],
) -> CodeDocument:
    path = FqnService.build_path(module_blueprint.path, is_package=False)
    imports_body = [
        import_def_to_ast_import_from(import_def, name_module_map)
        for import_def in module_blueprint.imports
    ]
    symbols_body = [symbol_def_to_ast_stmt(s) for s in module_blueprint.symbols]
    return CodeDocument(
        id=path,
        physical_path=path,
        body=imports_body + symbols_body,
        description=None,
    )
