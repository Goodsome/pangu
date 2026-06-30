from code_structure.domain.identities.symbol_ids import AttributeId, ClassId, FunctionId, MethodId, VariableId
from foundation.building_blocks.mutation_collector import Mutation
from foundation.common_types.identities.module_id import ModuleId


class AddModuleDefinesEdge(Mutation):
    source_id: ModuleId
    target_id: ClassId | FunctionId | VariableId


class AddClassDefinesEdge(Mutation):
    source_id: ClassId
    target_id: AttributeId | MethodId