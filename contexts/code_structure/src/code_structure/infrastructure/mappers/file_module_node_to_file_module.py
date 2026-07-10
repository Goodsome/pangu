import logging
from code_structure.domain.value_objects.parsed_import import ParsedImport
from foundation.common_types.fqns.fqn import ModuleFqn, SymbolFqn
from foundation.mappers.str_to_module_id import str_to_module_id

from code_structure.domain.aggregates.file_module import FileModule
from code_structure.domain.identities.symbol_ids import ClassId, FunctionId, VariableId
from code_structure.infrastructure.orm_models.file_module_node import FileNode


logger = logging.getLogger(__name__)


def file_module_node_to_file_module(file_module_node: FileNode) -> FileModule:
    classes = {
        ClassId.reconstitute(class_id.target_ref)
        for class_id in file_module_node.classes.items
    }
    functions = {
        FunctionId.reconstitute(function_id.target_ref)
        for function_id in file_module_node.functions.items
    }
    variables = {
        VariableId.reconstitute(variable_id.target_ref)
        for variable_id in file_module_node.variables.items
    }
    logger.info(f"Mapping file module node {file_module_node}")
    imports = [
        ParsedImport(
            target_fqn=SymbolFqn(import_edge.target_ref),
            alias=import_edge.alias,
        )
        for import_edge in file_module_node.imports.items
    ]
    return FileModule(
        id=str_to_module_id(file_module_node.id),
        name=file_module_node.name,
        fqn=ModuleFqn(file_module_node.fqn),
        classes=classes,
        functions=functions,
        variables=variables,
        imports=imports,
    )
