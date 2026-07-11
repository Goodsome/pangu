from architecture.domain.aggregates.file_module import FileModule
from architecture.domain.aggregates.package_module import PackageModule
from architecture.infrastructure.orm_models.module_node import (
    FileNode,
    PackageNode,
    DependsOnEdge,
    ContainsEdge,
)


def file_module_to_node(module: FileModule) -> FileNode:
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


def package_module_to_node(module: PackageModule) -> PackageNode:
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


def node_to_file_module(node: FileNode) -> FileModule:
    dependencies = {edge.target_ref for edge in node.dependencies.items}
    return FileModule.reconstitute(
        module_id=node.id,
        fqn=node.fqn,
        name=node.name,
        dependencies=dependencies,
    )


def node_to_package_module(node: PackageNode) -> PackageModule:
    dependencies = {edge.target_ref for edge in node.dependencies.items}
    contains = {edge.target_ref for edge in node.contains.items}
    return PackageModule.reconstitute(
        module_id=node.id,
        fqn=node.fqn,
        name=node.name,
        dependencies=dependencies,
        contains=contains,
    )
