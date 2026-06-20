from architecture.domain.identities.module_id import ModuleId
from codegen.shared.domain.core.mutation_collector import Mutation


class AddDependsEdgeMutation(Mutation):
    source: ModuleId
    target: ModuleId