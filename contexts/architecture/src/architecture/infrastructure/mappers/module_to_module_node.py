from architecture.domain.aggregates.module import Module
from architecture.infrastructure.orm_models.module_node import (
    FileNode,
    ModuleNode,
    PackageNode,
    DependsOnEdge,
    ContainsEdge,
)


def module_to_file_module_node(module: Module) -> FileNode:
    if module.is_package:
        raise ValueError("module is package")
    node = FileNode(
        id=str(module.id),
        name=module.name,
        fqn=module.fqn,
    )
    node.dependencies.items = [
        DependsOnEdge(source_ref=str(module.id), target_ref=str(d))
        for d in module.dependencies
    ]
    return node


def module_to_package_module_node(module: Module) -> PackageNode:
    if not module.is_package:
        raise ValueError("module is not package")
    node = PackageNode(
        id=str(module.id),
        name=module.name,
        fqn=module.fqn,
    )
    node.dependencies.items = [
        DependsOnEdge(source_ref=str(module.id), target_ref=str(d))
        for d in module.dependencies
    ]
    node.contains.items = [
        ContainsEdge(source_ref=str(module.id), target_ref=str(i))
        for i in module.contains
    ]
    return node


def module_to_module_node(module: Module) -> ModuleNode:
    match module.is_package:
        case True:
            return module_to_package_module_node(module)
        case False:
            return module_to_file_module_node(module)
