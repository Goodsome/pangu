from foundation.building_blocks.aggregate_root import AggregateRoot
from foundation.common_types.fqns.fqn import ModuleFqn
from foundation.common_types.identities.module_id import ModuleId


class Module(AggregateRoot[ModuleId]):
    fqn: ModuleFqn
    name: str
    
    