from code_structure.domain.aggregates.file_module import FileModule
from code_structure.infrastructure.orm_models.file_module_node import FileNode
from foundation.common_types.fqns.fqn import ModuleFqn
from foundation.mappers.str_to_module_id import str_to_module_id


def file_module_node_to_file_module(file_module_node: FileNode) -> FileModule:
    return FileModule(
        id=str_to_module_id(file_module_node.id),
        name=file_module_node.name,
        fqn=ModuleFqn(file_module_node.fqn),
    )
