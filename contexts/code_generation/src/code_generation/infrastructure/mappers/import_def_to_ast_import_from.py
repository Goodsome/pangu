from collections.abc import Mapping

from code_dom.domain.value_objects.ast_stmt import AstAlias, AstImportFrom

from code_generation.domain.value_objects.import_def import ImportDef


def import_def_to_ast_import_from(
    import_def: ImportDef,
    name_module_map: Mapping[str, str],
) -> AstImportFrom:
    if import_def.module_path:
        module = str(import_def.module_path)
    else:
        if import_def.name not in name_module_map:
            raise ValueError(f"Module not found for import: {import_def.name}")
        module = name_module_map[import_def.name]
    name = AstAlias(
        name=import_def.name,
        asname=import_def.alias,
    )
    return AstImportFrom(
        module=module,
        names=[name],
    )
