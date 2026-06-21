from architecture.domain.identities.module_id import ModuleId
from codegen.shared.domain.core.mutation_collector import Mutation


class AddContainsEdgeMutation(Mutation):
    source: ModuleId
    target: ModuleId
