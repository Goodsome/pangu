from architecture.domain.identities.module_id import ModuleId
from foundation.building_blocks.mutation_collector import Mutation


class RemoveDependsEdgeMutation(Mutation):
    source: ModuleId
    target: ModuleId
