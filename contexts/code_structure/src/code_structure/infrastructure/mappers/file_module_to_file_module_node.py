from code_structure.domain.aggregates.file_module import FileModule
from code_structure.infrastructure.orm_models.file_module_node import FileNode
from code_structure.infrastructure.orm_models.class_node import ClassNode
from code_structure.infrastructure.orm_models.function_node import FunctionNode
from code_structure.infrastructure.orm_models.variable_node import VariableNode
from code_structure.infrastructure.orm_models.symbol_node import SymbolNode

from foundation.persistence.orm.neo4j_base import OutEdge, EdgeItem
from code_structure.infrastructure.orm_models.edges import ImportsEdge, FileDefinesEdge


def file_module_to_file_module_node(file_module: FileModule) -> FileNode:
    file_id_str = str(file_module.id)

    classes: list[EdgeItem[FileDefinesEdge, ClassNode]] = [
        EdgeItem(edge=FileDefinesEdge(source_ref=file_id_str, target_ref=str(c_id)))
        for c_id in file_module.classes
    ]
    functions: list[EdgeItem[FileDefinesEdge, FunctionNode]] = [
        EdgeItem(edge=FileDefinesEdge(source_ref=file_id_str, target_ref=str(f_id)))
        for f_id in file_module.functions
    ]
    variables: list[EdgeItem[FileDefinesEdge, VariableNode]] = [
        EdgeItem(edge=FileDefinesEdge(source_ref=file_id_str, target_ref=str(v_id)))
        for v_id in file_module.variables
    ]
    imports: list[EdgeItem[ImportsEdge, SymbolNode]] = [
        EdgeItem(
            edge=ImportsEdge(
                source_ref=str(file_module.fqn),
                target_ref=str(imp.target_fqn),
                alias=imp.alias,
            )
        )
        for imp in file_module.imports
    ]

    return FileNode(
        id=file_id_str,
        name=file_module.name,
        fqn=file_module.fqn,
        classes=OutEdge(items=classes),
        functions=OutEdge(items=functions),
        variables=OutEdge(items=variables),
        imports=OutEdge(items=imports),
    )
