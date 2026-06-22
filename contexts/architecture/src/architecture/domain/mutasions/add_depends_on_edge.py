from architecture.domain.identities.module_id import ModuleId
from foundation.building_blocks.mutation_collector import Mutation


class AddDependsEdgeMutation(Mutation):
    source: ModuleId
    target: ModuleId
