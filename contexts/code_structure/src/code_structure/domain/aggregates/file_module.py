from pydantic import PrivateAttr
from code_structure.domain.identities.symbol_ids import ClassId, FunctionId, VariableId
from foundation.building_blocks.aggregate_root import AggregateRoot
from foundation.common_types.fqns.fqn import ModuleFqn
from foundation.common_types.identities.module_id import ModuleId


class FileModule(AggregateRoot[ModuleId]):
    fqn: ModuleFqn
    name: str
    
    _classes: set[ClassId] = PrivateAttr(default_factory=set)
    _functions: set[FunctionId] = PrivateAttr(default_factory=set)
    _variables: set[VariableId] = PrivateAttr(default_factory=set)