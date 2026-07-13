from typing import cast
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
        ClassId.reconstitute(target_ref)
        for target_ref in file_module_node.classes.get_edges_map()
    }
    functions = {
        FunctionId.reconstitute(target_ref)
        for target_ref in file_module_node.functions.get_edges_map()
    }
    variables = {
        VariableId.reconstitute(target_ref)
        for target_ref in file_module_node.variables.get_edges_map()
    }
    imports = [
        ParsedImport(
            target_fqn=SymbolFqn(target_ref),
            alias=cast(str | None, getattr(edge, "alias", None)),
        )
        for target_ref, edge in file_module_node.imports.get_edges_map().items()
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
