from architecture.domain.aggregates.module import Module
from architecture.infrastructure.orm_models.module_node import FileNode, ModuleNode, PackageNode


def module_to_file_module_node(module: Module) -> FileNode:
    if module.is_package:
        raise ValueError("module is package")
    return FileNode(
        id=str(module.id),
        name=module.name,
        fqn=module.fqn,
        dependencies=[str(d) for d in module.dependencies]
    )

def module_to_package_module_node(module: Module) -> PackageNode:
    if not module.is_package:
        raise ValueError("module is not package")
    return PackageNode(
        id=str(module.id),
        name=module.name,
        fqn=module.fqn,
        dependencies=[str(d) for d in module.dependencies],
        contains=[str(i) for i in module.contains]
    )

def module_to_module_node(module: Module) -> ModuleNode:
    match module.is_package:
        case True:
            return module_to_package_module_node(module)
        case False:
            return module_to_file_module_node(module)