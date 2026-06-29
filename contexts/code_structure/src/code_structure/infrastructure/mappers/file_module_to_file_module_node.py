from code_structure.domain.aggregates.file_module import FileModule
from code_structure.infrastructure.orm_models.file_module_node import FileModuleNode


def file_module_to_file_module_node(file_module: FileModule) -> FileModuleNode:
    
    return FileModuleNode(
        id=str(file_module.id),
        name=file_module.name,
        fqn=file_module.fqn,
    )