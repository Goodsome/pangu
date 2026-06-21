from architecture.domain.identities.module_id import ModuleId
from codegen.shared.domain.core.mutation_collector import Mutation


class RemoveContainsEdgeMutation(Mutation):
    source: ModuleId
    target: ModuleId
