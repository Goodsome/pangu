from code_structure.domain.aggregates.file_module import FileModule
from code_structure.infrastructure.orm_models.file_module_node import FileNode


from foundation.persistence.orm.neo4j_base import OutEdge
from code_structure.infrastructure.orm_models.edges import ImportsEdge, FileDefinesEdge


def file_module_to_file_module_node(file_module: FileModule) -> FileNode:
    classes = [
        FileDefinesEdge(source_ref=str(file_module.id), target_ref=str(c_id))
        for c_id in file_module.classes
    ]
    functions = [
        FileDefinesEdge(source_ref=str(file_module.id), target_ref=str(f_id))
        for f_id in file_module.functions
    ]
    variables = [
        FileDefinesEdge(source_ref=str(file_module.id), target_ref=str(v_id))
        for v_id in file_module.variables
    ]
    imports = [
        ImportsEdge(
            source_ref=str(file_module.fqn),
            target_ref=str(imp.target_fqn),
            alias=imp.alias,
        )
        for imp in file_module.imports
    ]

    return FileNode(
        id=str(file_module.id),
        name=file_module.name,
        fqn=file_module.fqn,
        classes=OutEdge(items=classes),
        functions=OutEdge(items=functions),
        variables=OutEdge(items=variables),
        imports=OutEdge(items=imports),
    )
