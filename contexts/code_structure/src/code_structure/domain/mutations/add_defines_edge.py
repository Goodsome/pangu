from code_structure.domain.identities.symbol_ids import (
    AttributeId,
    ClassId,
    FunctionId,
    MethodId,
    VariableId,
)
from foundation.building_blocks.mutation_collector import Mutation
from foundation.common_types.identities.module_id import ModuleId
from foundation.common_types.fqns.fqn import ModuleFqn, SymbolFqn


class AddModuleDefinesEdge(Mutation):
    source_id: ModuleId
    target_id: ClassId | FunctionId | VariableId


class AddClassDefinesEdge(Mutation):
    source_id: ClassId
    target_id: AttributeId | MethodId


class RemoveModuleDefinesEdge(Mutation):
    source_id: ModuleId
    target_id: ClassId | FunctionId | VariableId


class AddModuleImportsEdge(Mutation):
    source_fqn: ModuleFqn
    target_fqn: SymbolFqn
    alias: str | None = None


class AddReferencesEdge(Mutation):
    source_fqn: SymbolFqn
    target_fqn: SymbolFqn
