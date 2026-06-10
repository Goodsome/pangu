from codegen.code_metadata.domain.aggregates.code_node import ModuleNode


def get_import_from_module(
    origin_module: str | None, level: int, module_node: ModuleNode
) -> str:
    if level > 0:
        relative_level = level
        if module_node.is_package:
            relative_level = relative_level - 1
        module_prefix = module_node.get_parent_by_level(relative_level)
    else:
        module_prefix = ""
    module = origin_module or ""
    if module_prefix:
        module = module_prefix + "." + module
    if not module:
        raise ValueError(f"ImportFrom module is empty: {origin_module}")
    return module
